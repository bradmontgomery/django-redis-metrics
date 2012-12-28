"""
This app doesn't have any models, per se, but the following ``R`` class is a
lightweight wrapper around Redis.

"""
import datetime
import redis

from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.datastructures import SortedDict


class R(object):

    def __init__(self, *args, **kwargs):
        """Creates a connection to Redis, and sets the key used to store a
        set of slugs for all metrics.

        Valid keyword arguments:

        * ``metric_slugs_key`` -- The key storing a set of all metrics slugs
          (default is "metric-slugs")
        * ``gauge_slugs_key`` -- The key storing a set of all slugs for gauges
          (default is "gauge-slugs")
        * ``host`` -- Redis host (default settings.REDIS_METRICS_HOST)
        * ``port`` -- Redis port (default settings.REDIS_METRICS_PORT)
        * ``db``   -- Redis DB (default settings.REDIS_METRICS_DB)

        """
        self._metric_slugs_key = kwargs.get('metric_slugs_key', 'metric-slugs')
        self._gauge_slugs_key = kwargs.get('gauge_slugs_key', 'gauge-slugs')

        if 'host' in kwargs:
            self.host = kwargs['host']
        else:
            self.host = getattr(settings, 'REDIS_METRICS_HOST', 'localhost')

        if 'port' in kwargs:
            self.port = kwargs['port']
        else:
            self.port = int(getattr(settings, 'REDIS_METRICS_PORT', 6379))

        if 'db' in kwargs:
            self.db = kwargs['db']
        else:
            self.db = int(getattr(settings, 'REDIS_METRICS_DB', 0))

        # Create the connection to Redis
        self.r = redis.StrictRedis(host=self.host, port=self.port, db=self.db)

    def _date_range(self, since=None):
        """Returns a generator that yields ``datetime.date`` objects from the
        ``since`` date until *now*. If ``since`` is omitted, returns dates for
        one year.

        * ``since`` -- a ``datetime.date`` object or None.

        """
        now = datetime.date.today()
        if since is None:
            since_days = 365  # assume 1 year :-/
        else:
            delta = now - since  # The timedelta from "since" to "now"
            since_days = delta.days + 1
        return (now - datetime.timedelta(days=d) for d in range(since_days))

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
        patterns = SortedDict()
        patterns.insert(0, "daily",
            "m:{0}:{1}".format(slug, date.strftime("%Y-%m-%d")))
        patterns.insert(1, "weekly",
            "m:{0}:w:{1}".format(slug, date.strftime("%U")))
        patterns.insert(2, "monthly",
            "m:{0}:m:{1}".format(slug, date.strftime("%Y-%m")))
        patterns.insert(3, "yearly",
            "m:{0}:y:{1}".format(slug, date.strftime("%Y")))
        if granularity == 'all':
            return patterns.values()
        else:
            return [patterns[granularity]]

    def metric_slugs(self):
        """Return a set of metric slugs (i.e. those used to create Redis keys)
        for this app."""
        keys = self.r.smembers(self._metric_slugs_key)
        return set(s.split(":")[1] for s in keys)

    def metric(self, slug, num=1):
        """Records a metric, creating it if it doesn't exist or incrementing it
        if it does. All metrics are prefixed with 'm', and automatically
        aggregate for Day, Week, Month, and Year.

        Keys for each metric (slug) take the form:

            m:<slug>:<yyyy-mm-dd>   # Day
            m:<slug>:w:<num>        # Week
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

        Returns a list of dicts.

        NOTE: This method calls ``get_metric`` for each slug in the
        ``slug_list``, which really isn't very efficient.

        """
        results = []
        for slug in slug_list:
            results.append({slug: self.get_metric(slug)})
        return results

    def get_metric_history(self, slug, since=None, granularity='daily'):
        """Get history for a metric.

        * ``since`` -- the date from which we start pulling metrics
        * ``granularity`` -- daily, weekly, monthly, yearly

        Returns a list of tuples containing the Redis key and the associated
        metric::

            r = R()
            r.get_metric_history('test', granularity='weekly')
            [
                ('m:test:w:52', '15'),
            ]

        """
        keys = set()  # redis keys
        for date in self._date_range(since):
            keys.update(set(self._build_keys(slug, date, granularity)))
        return sorted(zip(keys, self.r.mget(keys)))

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
        k = self._gauge_key(slug)
        self.r.sadd(self._gauge_slugs_key, k)  # keep track of all Gauges
        self.r.set(k, current_value)

    def get_gauge(self, slug):
        k = self._gauge_key(slug)
        return self.r.get(k)
