"""
This app doesn't have any models, per se, but the following ``R`` class is a
lightweight wrapper around Redis.

"""
import datetime
import redis

from django.conf import settings
from django.template.defaultfilters import slugify


class R(object):

    def __init__(self, *args, **kwargs):
        self.r = redis.StrictRedis(
            host=getattr(settings, 'REDIS_METRICS_HOST', 'localhost'),
            port=int(getattr(settings, 'REDIS_METRICS_PORT', 6379)),
            db=int(getattr(settings, 'REDIS_METRICS_DB', 0)),
        )

    def _build_keys(self, slug):
        """Builds various keys for the given slug."""
        slug = slugify(slug)
        now = datetime.datetime.now()
        keys = [
            "m:{0}:{1}".format(slug, now.strftime("%Y-%m-%d")),  # Day
            "m:{0}:w:{1}".format(slug, now.strftime("%U")),      # Week
            "m:{0}:m:{1}".format(slug, now.strftime("%Y-%m")),   # Month
            "m:{0}:y:{1}".format(slug, now.strftime("%Y")),      # Year
        ]
        return keys

    def slugs(self):
        """Return a set of metric slugs (i.e. those used to create Redis keys)
        for this app."""
        # TODO: automactially keep a list (or set) of all slugs, so we don't
        # have to do a full scan when we decide to list the keys.
        return list(set([k.split(":")[1] for k in self.r.keys()]))

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

        # Increment keys. NOTE: current redis-py (2.7.2) doesn't include an
        # incrby method, so let's brute-force it for now.
        for i in range(num):
            self.r.incr(day_key)
            self.r.incr(week_key)
            self.r.incr(month_key)
            self.r.incr(year_key)

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

        """
        # TODO: there's probably a better way to get this data from Redis.
        results = []
        for slug in slug_list:
            results.append({slug: self.get_metric(slug)})
        return results

    # Gagues. Gagues have a different prefix "g:" in order to differentiate
    # them from a metric of the same name.

    def _gague_key(self, slug):
        return "g:{0}".format(slugify(slug))

    def gague(self, slug, current_value):
        k = self._gague_key(slug)
        self.r.set(k, current_value)

    def get_gague(self, slug):
        k = self._gague_key(slug)
        return self.r.get(k)
