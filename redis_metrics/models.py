"""
This app doesn't have any models, per se, but the following ``R`` class is a
lightweight wrapper around Redis.

"""
from __future__ import unicode_literals
import redis

from importlib import import_module
from collections import OrderedDict
from datetime import datetime, timedelta
from django.template.defaultfilters import slugify

from .settings import app_settings, GRANULARITIES
from .templatetags import redis_metrics_filters as template_tags


def dedupe(items):
    """Remove duplicates from a sequence (of hashable items) while maintaining
    order. NOTE: This only works if items in the list are hashable types.

    Taken from the Python Cookbook, 3rd ed. Such a great book!

    """
    seen = set()
    for item in items:
        if item not in seen:
            yield item
            seen.add(item)


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
        * ``connection_class`` -- class to use to obtain a Redis connection (set in settings.REDIS_METRICS['CONNECTION_CLASS'])
        * ``host`` -- Redis host (set in settings.REDIS_METRICS['HOST'])
        * ``port`` -- Redis port (set in settings.REDIS_METRICS['PORT'])
        * ``db`` -- Redis DB (set in settings.REDIS_METRICS['DB'])
        * ``password`` -- Redis password (set in settings.REDIS_METRICS['PASSWORD'])
        * ``socket_timeout``   -- Redis password (set in
          settings.REDIS_METRICS['SOCKET_TIMEOUT'])
        * ``connection_pool`` -- Redis connection pool info. (set in
          settings.REDIS_METRICS['SOCKET_CONNECTION_POOL'])

        """
        self._categories_key = kwargs.get('categories_key', 'categories')
        self._metric_slugs_key = kwargs.get('metric_slugs_key', 'metric-slugs')
        self._gauge_slugs_key = kwargs.get('gauge_slugs_key', 'gauge-slugs')

        self.connection_class = kwargs.pop('connection_class', app_settings.CONNECTION_CLASS)

        if self.connection_class:
            package, module = self.connection_class.rsplit('.', 1)
            self.r = getattr(import_module(package), module)()
        else:
            self.host = kwargs.pop('host', app_settings.HOST)
            self.port = kwargs.pop('port', app_settings.PORT)
            self.db = kwargs.pop('db', app_settings.DB)
            self.password = kwargs.pop('password', app_settings.PASSWORD)
            self.socket_timeout = kwargs.pop(
                'socket_timeout',
                app_settings.SOCKET_TIMEOUT
            )
            self.connection_pool = kwargs.pop(
                'connection_pool',
                app_settings.SOCKET_CONNECTION_POOL
            )

            # Create the connection to Redis
            self.r = redis.StrictRedis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                socket_timeout=self.socket_timeout,
                connection_pool=self.connection_pool,
                decode_responses=True
            )

    def _date_range(self, granularity, since, to=None):
        """Returns a generator that yields ``datetime.datetime`` objects from
        the ``since`` date until ``to`` (default: *now*).

        * ``granularity`` -- The granularity at which the generated datetime
          objects should be created: seconds, minutes, hourly, daily, weekly,
          monthly, or yearly
        * ``since`` -- a ``datetime.datetime`` object, from which we start
          generating periods of time. This can also be ``None``, and will
          default to the past 7 days if that's the case.
        * ``to`` -- a ``datetime.datetime`` object, from which we start
          generating periods of time. This can also be ``None``, and will
          default to now if that's the case.

        If ``granularity`` is one of daily, weekly, monthly, or yearly, this
        function gives objects at the daily level.

        If ``granularity`` is one of the following, the number of datetime
        objects returned is capped, otherwise this code is really slow and
        probably generates more data than we want:

            * hourly: returns at most 720 values (~30 days)
            * minutes: returns at most 480 values (8 hours)
            * second: returns at most 300 values (5 minutes)

        For example, if granularity is "seconds", we'll receive datetime
        objects that differ by 1 second each.

        """
        if since is None:
            since = datetime.utcnow() - timedelta(days=7)  # Default to 7 days

        if to is None:
            to = datetime.utcnow()
        elapsed = (to - since)

        # Figure out how many units to generate for the elapsed time.
        # I'm going to use `granularity` as a keyword parameter to timedelta,
        # so I need to change the wording for hours and anything > days.
        if granularity == "seconds":
            units = elapsed.total_seconds()
            units = 300 if units > 300 else units
        elif granularity == "minutes":
            units = elapsed.total_seconds() / 60
            units = 480 if units > 480 else units
        elif granularity == "hourly":
            granularity = "hours"
            units = elapsed.total_seconds() / 3600
            units = 720 if units > 720 else units
        else:
            granularity = "days"
            units = elapsed.days + 1

        return (to - timedelta(**{granularity: u}) for u in range(int(units)))

    def categories(self):
        """Returns a set of Categories under which metrics may have been
        organized."""
        return self.r.smembers(self._categories_key)

    def _category_key(self, category):
        return u"c:{0}".format(category)

    def _category_slugs(self, category):
        """Returns a set of the metric slugs for the given category"""
        key = self._category_key(category)
        slugs = self.r.smembers(key)
        return slugs

    def _categorize(self, slug, category):
        """Add the ``slug`` to the ``category``. We store category data as
        as set, with a key of the form::

            c:<category name>

        The data is set of metric slugs::

            "slug-a", "slug-b", ...

        """
        key = self._category_key(category)
        self.r.sadd(key, slug)

        # Store all category names in a Redis set, for easy retrieval
        self.r.sadd(self._categories_key, category)

    def _granularities(self):
        """Returns a generator of all possible granularities based on the
        MIN_GRANULARITY and MAX_GRANULARITY settings.
        """
        keep = False
        for g in GRANULARITIES:
            if g == app_settings.MIN_GRANULARITY and not keep:
                keep = True
            elif g == app_settings.MAX_GRANULARITY and keep:
                keep = False
                yield g
            if keep:
                yield g

    def _metric_key_patterns(self):
        """ The Redis metric key and date formatting patterns for each key, by granularity"""
        return {
            "seconds": {"key": "m:{0}:s:{1}", "date_format": "%Y-%m-%d-%H-%M-%S"},
            "minutes": {"key": "m:{0}:i:{1}", "date_format": "%Y-%m-%d-%H-%M"},
            "hourly": {"key": "m:{0}:h:{1}", "date_format": "%Y-%m-%d-%H"},
            "daily": {"key": "m:{0}:{1}", "date_format": "%Y-%m-%d"},
            "weekly": {
                "key": "m:{0}:w:{1}",
                "date_format": "%Y-%{0}".format('W' if app_settings.MONDAY_FIRST_DAY_OF_WEEK else 'U')
            },
            "monthly": {"key": "m:{0}:m:{1}", "date_format": "%Y-%m"},
            "yearly": {"key": "m:{0}:y:{1}", "date_format": "%Y"},
        }

    def _build_key_patterns(self, slug, date):
        """Builds an OrderedDict of metric keys and patterns for the given slug
        and date."""
        # we want to keep the order, from smallest to largest granularity
        patts = OrderedDict()
        metric_key_patterns = self._metric_key_patterns()
        for g in self._granularities():
            date_string = date.strftime(metric_key_patterns[g]["date_format"])
            patts[g] = metric_key_patterns[g]["key"].format(slug, date_string)
        return patts

    def _build_keys(self, slug, date=None, granularity='all'):
        """Builds redis keys used to store metrics.

        * ``slug`` -- a slug used for a metric, e.g. "user-signups"
        * ``date`` -- (optional) A ``datetime.datetime`` object used to
          generate the time period for the metric. If omitted, the current date
          and time (in UTC) will be used.
        * ``granularity`` -- Must be one of: "all" (default), "yearly",
        "monthly", "weekly", "daily", "hourly", "minutes", or "seconds".

        Returns a list of strings.

        """
        slug = slugify(slug)  # Ensure slugs have a consistent format
        if date is None:
            date = datetime.utcnow()
        patts = self._build_key_patterns(slug, date)
        if granularity == "all":
            return list(patts.values())
        return [patts[granularity]]

    def metric_slugs(self):
        """Return a set of metric slugs (i.e. those used to create Redis keys)
        for this app."""
        return self.r.smembers(self._metric_slugs_key)

    def metric_slugs_by_category(self):
        """Return a dictionary of metrics data indexed by category:

            {<category_name>: set(<slug1>, <slug2>, ...)}

        """
        result = OrderedDict()
        categories = sorted(self.r.smembers(self._categories_key))
        for category in categories:
            result[category] = self._category_slugs(category)

        # We also need to see the uncategorized metric slugs, so need some way
        # to check which slugs are not already stored.
        categorized_metrics = set([  # Flatten the list of metrics
            slug for sublist in result.values() for slug in sublist
        ])
        f = lambda slug: slug not in categorized_metrics
        uncategorized = list(set(filter(f, self.metric_slugs())))
        if len(uncategorized) > 0:
            result['Uncategorized'] = uncategorized
        return result

    def delete_metric(self, slug):
        """Removes all keys for the given ``slug``."""

        # To remove all keys for a slug, I need to retrieve them all from
        # the set of metric keys, This uses the redis "keys" command, which is
        # inefficient, but this shouldn't be used all that often.
        prefix = "m:{0}:*".format(slug)
        keys = self.r.keys(prefix)
        self.r.delete(*keys)  # Remove the metric data

        # Finally, remove the slug from the set
        self.r.srem(self._metric_slugs_key, slug)

    def set_metric(self, slug, value, category=None, expire=None, date=None):
        """Assigns a specific value to the *current* metric. You can use this
        to start a metric at a value greater than 0 or to reset a metric.

        The given slug will be used to generate Redis keys at the following
        granularities: Seconds, Minutes, Hours, Day, Week, Month, and Year.

        Parameters:

        * ``slug`` -- a unique value to identify the metric; used in
          construction of redis keys (see below).
        * ``value`` -- The value of the metric.
        * ``category`` -- (optional) Assign the metric to a Category (a string)
        * ``expire`` -- (optional) Specify the number of seconds in which the
          metric will expire.
        * ``date`` -- (optional) Specify the timestamp for the metric; default
          used to build the keys will be the current date and time in UTC form.

        Redis keys for each metric (slug) take the form:

            m:<slug>:s:<yyyy-mm-dd-hh-mm-ss> # Second
            m:<slug>:i:<yyyy-mm-dd-hh-mm>    # Minute
            m:<slug>:h:<yyyy-mm-dd-hh>       # Hour
            m:<slug>:<yyyy-mm-dd>            # Day
            m:<slug>:w:<yyyy-num>            # Week (year - week number)
            m:<slug>:m:<yyyy-mm>             # Month
            m:<slug>:y:<yyyy>                # Year

        """
        keys = self._build_keys(slug, date=date)

        # Add the slug to the set of metric slugs
        self.r.sadd(self._metric_slugs_key, slug)

        # Construct a dictionary of key/values for use with mset
        data = {}
        for k in keys:
            data[k] = value
        self.r.mset(data)

        # Add the category if applicable.
        if category:
            self._categorize(slug, category)

        # Expire the Metric in ``expire`` seconds if applicable.
        if expire:
            for k in keys:
                self.r.expire(k, expire)

    def metric(self, slug, num=1, category=None, expire=None, date=None):
        """Records a metric, creating it if it doesn't exist or incrementing it
        if it does. All metrics are prefixed with 'm', and automatically
        aggregate for Seconds, Minutes, Hours, Day, Week, Month, and Year.

        Parameters:

        * ``slug`` -- a unique value to identify the metric; used in
          construction of redis keys (see below).
        * ``num`` -- Set or Increment the metric by this number; default is 1.
        * ``category`` -- (optional) Assign the metric to a Category (a string)
        * ``expire`` -- (optional) Specify the number of seconds in which the
          metric will expire.
        * ``date`` -- (optional) Specify the timestamp for the metric; default
          used to build the keys will be the current date and time in UTC form.

        Redis keys for each metric (slug) take the form:

            m:<slug>:s:<yyyy-mm-dd-hh-mm-ss> # Second
            m:<slug>:i:<yyyy-mm-dd-hh-mm>    # Minute
            m:<slug>:h:<yyyy-mm-dd-hh>       # Hour
            m:<slug>:<yyyy-mm-dd>            # Day
            m:<slug>:w:<yyyy-num>            # Week (year - week number)
            m:<slug>:m:<yyyy-mm>             # Month
            m:<slug>:y:<yyyy>                # Year

        """
        # Add the slug to the set of metric slugs
        self.r.sadd(self._metric_slugs_key, slug)

        if category:
            self._categorize(slug, category)

        # Increment keys. NOTE: current redis-py (2.7.2) doesn't include an
        # incrby method; .incr accepts a second ``amount`` parameter.
        keys = self._build_keys(slug, date=date)

        # Use a pipeline to speed up incrementing multiple keys
        pipe = self.r.pipeline()
        for key in keys:
            pipe.incr(key, num)
            if expire:
                pipe.expire(key, expire)
        pipe.execute()

    def get_metric(self, slug):
        """Get the current values for a metric.

        Returns a dictionary with metric values accumulated for the seconds,
        minutes, hours, day, week, month, and year.

        """
        results = OrderedDict()
        granularities = self._granularities()
        keys = self._build_keys(slug)
        for granularity, key in zip(granularities, keys):
            results[granularity] = self.r.get(key)
        return results

    def get_metrics(self, slug_list):
        """Get the metrics for multiple slugs.

        Returns a list of two-tuples containing the metric slug and a
        dictionary like the one returned by ``get_metric``::

            (
                some-metric, {
                    'seconds': 0, 'minutes': 0, 'hours': 0,
                    'day': 0, 'week': 0, 'month': 0, 'year': 0
                }
            )

        """
        # meh. I should have been consistent here, but I'm lazy, so support these
        # value names instead of granularity names, but respect the min/max
        # granularity settings.
        keys = ['seconds', 'minutes', 'hours', 'day', 'week', 'month', 'year']
        key_mapping = {gran: key for gran, key in zip(GRANULARITIES, keys)}
        keys = [key_mapping[gran] for gran in self._granularities()]

        results = []
        for slug in slug_list:
            metrics = self.r.mget(*self._build_keys(slug))
            if any(metrics):  # Only if we have data.
                results.append((slug, dict(zip(keys, metrics))))
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
        key = self._category_key(category)
        if len(metric_slugs) == 0:
            # If there are no metrics, just remove the category
            self.delete_category(category)
        else:
            # Save all the slugs in the category, and save the category name
            self.r.sadd(key, *metric_slugs)
            self.r.sadd(self._categories_key, category)

    def get_metric_history(self, slugs, since=None, to=None, granularity='daily'):
        """Get history for one or more metrics.

        * ``slugs`` -- a slug OR a list of slugs
        * ``since`` -- the date from which we start pulling metrics
        * ``to`` -- the date until which we start pulling metrics
        * ``granularity`` -- seconds, minutes, hourly,
                             daily, weekly, monthly, yearly

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
        keys = []
        for slug in slugs:
            for date in self._date_range(granularity, since, to):
                keys += self._build_keys(slug, date, granularity)
        keys = list(dedupe(keys))

        # Fetch our data, replacing any None-values with zeros
        results = [0 if v is None else v for v in self.r.mget(keys)]
        results = zip(keys, results)
        return sorted(results, key=lambda t: t[0])

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
        history = self.get_metric_history(slugs, since, granularity=granularity)
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

        # Finally, stick the time periods in the first column.
        _history.insert(0, periods)
        return list(zip(*_history))  # Transpose the rows & columns

    def get_metric_history_chart_data(self, slugs, since=None, granularity='daily'):
        """Provides the same data as ``get_metric_history``, but with metrics
        data arranged in a format that's easy to plot with Chart.js. If you had
        the following yearly history, for example::

            [
                ('m:bar:y:2012', '1'),
                ('m:bar:y:2013', '2'),
                ('m:bar:y:2014', '3'),
                ('m:foo:y:2012', '4'),
                ('m:foo:y:2013', '5')
                ('m:foo:y:2014', '6')
            ]

        this method would provide you with the following data structure::

            'periods': ['y:2012', 'y:2013', 'y:2014']
            'data': [
              {
                'slug': 'bar',
                'values': [1, 2, 3]
              },
              {
                'slug': 'foo',
                'values': [4, 5, 6]
              },
            ]

        """
        slugs = sorted(slugs)
        history = self.get_metric_history(slugs, since, granularity=granularity)

        # Convert the history into an intermediate data structure organized
        # by periods. Since the history is sorted by key (which includes both
        # the slug and the date, the values should be ordered correctly.
        periods = []
        data = OrderedDict()
        for k, v in history:
            period = template_tags.strip_metric_prefix(k)
            if period not in periods:
                periods.append(period)

            slug = template_tags.metric_slug(k)
            if slug not in data:
                data[slug] = []
            data[slug].append(v)

        # Now, reorganize data for our end result.
        metrics = {'periods': periods, 'data': []}
        for slug, values in data.items():
            metrics['data'].append({
                'slug': slug,
                'values': values
            })

        return metrics  # templates still don't like defaultdict's

    # Gauges. Gauges have a different prefix "g:" in order to differentiate
    # them from a metric of the same name.
    def gauge_slugs(self):
        """Return a set of Gauges slugs (i.e. those used to create Redis keys)
        for this app."""
        return self.r.smembers(self._gauge_slugs_key)

    def _gauge_key(self, slug):
        """Make sure our slugs have a consistent format."""
        return "g:{0}".format(slugify(slug))

    def gauge(self, slug, current_value):
        """Set the value for a Gauge.

        * ``slug`` -- the unique identifier (or key) for the Gauge
        * ``current_value`` -- the value that the gauge should display

        """
        k = self._gauge_key(slug)
        self.r.sadd(self._gauge_slugs_key, slug)  # keep track of all Gauges
        self.r.set(k, current_value)

    def get_gauge(self, slug):
        k = self._gauge_key(slug)
        return self.r.get(k)

    def delete_gauge(self, slug):
        """Removes all gauges with the given ``slug``."""
        key = self._gauge_key(slug)
        self.r.delete(key)  # Remove the Gauge
        self.r.srem(self._gauge_slugs_key, slug)  # Remove from the set of keys
