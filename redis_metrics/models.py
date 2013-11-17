"""
This app doesn't have any models, per se, but the following ``R`` class is a
lightweight wrapper around Redis.

"""
from collections import OrderedDict
import datetime
import json
import redis

from django.conf import settings
from django.template.defaultfilters import slugify

from .templatetags import redis_metrics_filters as template_tags


class R(object):

    def __init__(self, **kwargs):
        """Creates a connection to Redis, and sets the key used to store a
        set of slugs for all metrics.

        Valid keyword arguments:

        * ``categories_key`` -- The key storing a set of all metric Categories
          (default is "categories")
        * ``metric_slugs_key`` -- The key storing a set of all metrics slugs
          (default is "metric-slugs")
        * ``gauge_slugs_key`` -- The key storing a set of all slugs for gauges
          (default is "gauge-slugs")
        * ``host`` -- Redis host (default settings.REDIS_METRICS_HOST)
        * ``port`` -- Redis port (default settings.REDIS_METRICS_PORT)
        * ``db``   -- Redis DB (default settings.REDIS_METRICS_DB)
        * ``password``   -- Redis password
          (default settings.REDIS_METRICS_PASSWORD)
        * ``socket_timeout``   -- Redis password
          (default settings.REDIS_METRICS_SOCKET_TIMEOUT)
        * ``connection_pool``   -- Redis password
          (default settings.REDIS_METRICS_SOCKET_CONNECTION_POOL)

        """
        self._categories_key = kwargs.get('categories_key', 'categories')
        self._metric_slugs_key = kwargs.get('metric_slugs_key', 'metric-slugs')
        self._gauge_slugs_key = kwargs.get('gauge_slugs_key', 'gauge-slugs')

        self.host = kwargs.pop(
            'host',
            getattr(settings, 'REDIS_METRICS_HOST', 'localhost'))

        self.port = kwargs.pop(
            'port',
            int(getattr(settings, 'REDIS_METRICS_PORT', 6379)))

        self.db = kwargs.pop(
            'db',
            int(getattr(settings, 'REDIS_METRICS_DB', 0)))

        self.password = kwargs.pop(
            'password', getattr(settings, 'REDIS_METRICS_PASSWORD', None))

        self.socket_timeout = kwargs.pop(
            'socket_timeout',
            getattr(settings, 'REDIS_METRICS_SOCKET_TIMEOUT', None))

        self.connection_pool = kwargs.pop(
            'connection_pool',
            getattr(settings, 'REDIS_METRICS_SOCKET_CONNECTION_POOL', None))

        # Create the connection to Redis
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=self.db,
                                   password=self.password,
                                   socket_timeout=self.socket_timeout,
                                   connection_pool=self.connection_pool)

    def _date_range(self, since=None):
        """Returns a generator that yields ``datetime.datetime`` objects from
        the ``since`` date until *now*. If ``since`` is omitted, returns dates
        for one year.

        * ``since`` -- a ``datetime.datetime`` object or None.

        """
        now = datetime.datetime.today()
        if since is None:
            since_days = 365  # assume 1 year :-/
        else:
            delta = now - since  # The timedelta from "since" to "now"
            since_days = delta.days + 1
        return (now - datetime.timedelta(days=d) for d in range(since_days))

    def _category_key(self, category):
        return u"c:{0}".format(category)

    def _category_slugs(self, category):
        """Returns a list of the metric slugs for the given category"""
        key = self._category_key(category)
        slugs = self.r.get(key)
        return [] if slugs is None else json.loads(slugs)

    def _categorize(self, slug, category):
        """Add the ``slug`` to the ``category``. We store category data as
        JSON strings, with a key of the form::

            c:<category name>

        The data is a JSON-serialized list of metric slugs::

            '["slug-a", "slug-b", ...]'

        """
        # Store existing slugs in a set, so we don't have duplicates
        metric_slugs = set(self._category_slugs(category))
        metric_slugs.add(slug)

        # sets are not JSON-serializable, so convert to a list before storing
        json_data = json.dumps(list(metric_slugs))
        key = self._category_key(category)
        self.r.set(key, json_data)

        # Store all category names in a Redis set, for easy retrieval
        self.r.sadd(self._categories_key, category)

    def _build_keys(self, slug, date=None, granularity='all'):
        """Builds redis keys used to store metrics.

        * ``slug`` -- a slug used for a metric, e.g. "user-signups"
        * ``date`` -- (optional) A ``datetime.date`` or ``datetime.datetime``
          objects used to generate the time period for the metric. If omitted,
          the current date will be used.
        * ``granularity`` -- Must be one of: "all" (default), "daily",
          "weekly", "monthly", "yearly".

        Returns a list of strings.

        """
        slug = slugify(slug)  # Make sure our slugs have a consistent format
        if date is None:
            date = datetime.date.today()

        # we want to keep the order, here: daily, weekly, monthly, yearly
        patts = OrderedDict()
        patts["daily"] = "m:{0}:{1}".format(slug, date.strftime("%Y-%m-%d"))
        patts["weekly"] = "m:{0}:w:{1}".format(slug, date.strftime("%Y-%U"))
        patts["monthly"] = "m:{0}:m:{1}".format(slug, date.strftime("%Y-%m"))
        patts["yearly"] = "m:{0}:y:{1}".format(slug, date.strftime("%Y"))

        if granularity == 'all':
            return patts.values()
        else:
            return [patts[granularity]]

    def metric_slugs(self):
        """Return a set of metric slugs (i.e. those used to create Redis keys)
        for this app."""
        keys = self.r.smembers(self._metric_slugs_key)
        return set(s.split(":")[1] for s in keys)

    def metric_slugs_by_category(self):
        """Return a dictionary of category->metrics data:

            {<category_name>: [<slug1>, <slug2>, ...]}

        """
        result = {}
        categories = self.r.smembers(self._categories_key)
        for category in categories:
            result[category] = self._category_slugs(category)

        # We also need to see the uncategorized metric slugs, so need some way
        # to check which slugs are not already stored.
        categorized_metrics = set([  # Flatten the list of metrics
            slug for sublist in result.values() for slug in sublist
        ])
        f = lambda slug: slug not in categorized_metrics
        uncategorized = filter(f, self.metric_slugs())
        if len(uncategorized) > 0:
            result['Uncategorized'] = uncategorized
        return result

    def delete_metric(self, slug):
        """Removes all keys for the given ``slug``."""

        # To remove all keys for a slug, I need to retrieve them all from
        # the set of metric keys, then filter the matching prefixes.
        # This is quite possibly the most inefficient way to do this :-/
        prefix = "m:{0}:".format(slug)
        keys = [
            k for k in self.r.smembers(self._metric_slugs_key)
            if k.startswith(prefix)
        ]

        # Remove the metric data
        self.r.delete(*keys)

        # Finally, remove keys from the set
        self.r.srem(self._metric_slugs_key, *keys)

    def metric(self, slug, num=1, category=None, expire=None):
        """Records a metric, creating it if it doesn't exist or incrementing it
        if it does. All metrics are prefixed with 'm', and automatically
        aggregate for Day, Week, Month, and Year.

        Parameters:

        * ``slug`` -- a unique value to identify the metric; used in
          construction of redis keys (see below).
        * ``num`` -- Set or Increment the metric by this number; default is 1.
        * ``category`` -- (optional) Assign the metric to a Category (a string)
        * ``expire`` -- (optional) Specify the number of seconds in which the
          metric will expire.

        Redis keys for each metric (slug) take the form:

            m:<slug>:<yyyy-mm-dd>   # Day
            m:<slug>:w:<yyyy-num>   # Week (year - week number)
            m:<slug>:m:<yyyy-mm>    # Month
            m:<slug>:y:<yyyy>       # Year

        """
        day_key, week_key, month_key, year_key = self._build_keys(slug)

        # Keep track of all of our keys
        self.r.sadd(self._metric_slugs_key,
                    day_key, week_key, month_key, year_key)

        # Increment keys. NOTE: current redis-py (2.7.2) doesn't include an
        # incrby method; .incr accepts a second ``amound`` parameter.
        self.r.incr(day_key, num)
        self.r.incr(week_key, num)
        self.r.incr(month_key, num)
        self.r.incr(year_key, num)

        if category:
            self._categorize(slug, category)

        # Expire the Metric in ``expire`` seconds
        if expire:
            self.r.expire(day_key, expire)
            self.r.expire(week_key, expire)
            self.r.expire(month_key, expire)
            self.r.expire(year_key, expire)

    def get_metric(self, slug):
        """Get the current values for a metric.

        Returns a dict with metric values accumulated for the day, week, month,
        and year.

        """
        day_key, week_key, month_key, year_key = self._build_keys(slug)
        return {
            'day': self.r.get(day_key),
            'week': self.r.get(week_key),
            'month': self.r.get(month_key),
            'year': self.r.get(year_key),
        }

    def get_metrics(self, slug_list):
        """Get the metrics for multiple slugs.

        Returns a list of two-tuples containing the metric slug and a
        dictionary like the one returned by ``get_metric``::

            (some-metric, {'day': 0, 'week': 0, 'month': 0, 'year': 0})

        NOTE: This method calls ``get_metric`` for each slug in the
        ``slug_list``, which really isn't very efficient.

        """
        results = []
        for slug in slug_list:
            results.append((slug, self.get_metric(slug)))
        return results

    def get_category_metrics(self, category):
        """Get metrics belonging to the given category"""
        slug_list = self._category_slugs(category)
        return self.get_metrics(slug_list)

    def delete_category(self, category):
        """Removes the category from Redis. This doesn't touch the metrics;
        they simply become uncategorized."""
        # Remove mapping of metrics-to-category
        category_key = self._category_key(category)
        self.r.delete(category_key)

        # Remove category from Set
        self.r.srem(self._categories_key, category)

    def reset_category(self, category, metric_slugs):
        """Resets (or creates) a category containing a list of metrics.

        * ``category`` -- A category name
        * ``metric_slugs`` -- a list of all metrics that are members of the
            category.

        """
        if len(metric_slugs) == 0:
            # If there are no metrics, just remove the category
            self.delete_category(category)
        else:
            # Convert metrics to json (removing any duplicates)
            json_data = json.dumps(list(metric_slugs))
            self.r.set(self._category_key(category), json_data)

            # Store all category names in a Redis set, for easy retrieval
            self.r.sadd(self._categories_key, category)

    def get_metric_history(self, slugs, since=None, granularity='daily'):
        """Get history for one or more metrics.

        * ``slugs`` -- a slug OR a list of slugs
        * ``since`` -- the date from which we start pulling metrics
        * ``granularity`` -- daily, weekly, monthly, yearly

        Returns a list of tuples containing the Redis key and the associated
        metric::

            r = R()
            r.get_metric_history('test', granularity='weekly')
            [
                ('m:test:w:2012-52', '15'),
            ]

        To get history for multiple metrics, just provide a list of slugs::

            metrics = ['test', 'other']
            r.get_metric_history(metrics, granularity='weekly')
            [
                ('m:test:w:2012-52', '15'),
                ('m:other:w:2012-52', '42'),
            ]

        """
        if not type(slugs) == list:
            slugs = [slugs]

        # Build the set of Redis keys that we need to get.
        keys = set()
        for slug in slugs:
            for date in self._date_range(since):
                keys.update(set(self._build_keys(slug, date, granularity)))
        return sorted(zip(keys, self.r.mget(keys)))

    def get_metric_history_as_columns(self, slugs, since=None,
                                      granularity='daily'):
        """Provides the same data as ``get_metric_history``, but in a columnar
        format. If you had the following yearly history, for example::

            [
                ('m:bar:y:2012', '1'),
                ('m:bar:y:2013', '2'),
                ('m:foo:y:2012', '3'),
                ('m:foo:y:2013', '4')
            ]

        this method would provide you with the following data structure::

            [
                ['Period',  'bar',  'foo']
                ['y:2012',  '1',    '3'],
                ['y:2013',  '2',    '4'],
            ]

        Note that this also includes a header column. Data in this format may
        be useful for certain graphing libraries (I'm looking at you Google
        Charts LineChart).

        """
        history = self.get_metric_history(slugs, since, granularity)
        _history = []  # new, columnar history
        periods = ['Period']  # A separate, single column for the time period
        for s in slugs:
            column = [s]  # story all the data for a single slug
            for key, value in history:
                # ``metric_slug`` extracts the slug from the Redis Key
                if template_tags.metric_slug(key) == s:
                    column.append(value)

                # Get time period value as first column; This value is
                # duplicated in the Redis key for each value, so this is a bit
                # inefficient, but... oh well.
                period = template_tags.strip_metric_prefix(key)
                if period not in periods:
                    periods.append(period)

            _history.append(column)  # Remember that slug's column of data
        _history.insert(0, periods)  # Finally, stick the time periods in the
                                     # first column.
        return zip(*_history)  # Transpose the rows & columns

    # Gauges. Gauges have a different prefix "g:" in order to differentiate
    # them from a metric of the same name.
    def gauge_slugs(self):
        """Return a set of Gauges slugs (i.e. those used to create Redis keys)
        for this app."""
        keys = self.r.smembers(self._gauge_slugs_key)
        return set(s.split(":")[1] for s in keys)

    def _gauge_key(self, slug):
        """Make sure our slugs have a consistent format."""
        return "g:{0}".format(slugify(slug))

    def gauge(self, slug, current_value):
        """Set the value for a Gauge.

        * ``slug`` -- the unique identifier (or key) for the Gauge
        * ``current_value`` -- the value that the gauge should display

        """
        k = self._gauge_key(slug)
        self.r.sadd(self._gauge_slugs_key, k)  # keep track of all Gauges
        self.r.set(k, current_value)

    def get_gauge(self, slug):
        k = self._gauge_key(slug)
        return self.r.get(k)

    def delete_gauge(self, slug):
        """Removes all gauges with the given ``slug``."""
        key = self._gauge_key(slug)
        self.r.delete(key)  # Remove the Gauge
        self.r.srem(self._gauge_slugs_key, key)  # Remove from the set of keys
