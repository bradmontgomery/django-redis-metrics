"""
This command essentially migrates data used for a number of items used by
the R class. This should fix any issues related to:

    WRONGTYPE Operation against a key holding the wrong kind of value

These include:

*

"""
from __future__ import unicode_literals
import json

from django.core.management.base import NoArgsCommand
from redis.exceptions import ResponseError
from redis_metrics.utils import get_r


class Command(NoArgsCommand):
    help = "Fixes backward-incompatible changes to the way we store some keys in Redis"

    def handle_noargs(self, *args, **options):
        r = get_r()

        # Store *only* slugs in the Set of metric slugs. Prior to this, we
        # stored metric keys, and split the slug from the key upon retrieval
        try:
            keys = r.r.smembers(r._metric_slugs_key)
            slugs = set(s.split(":")[1] for s in keys)
            r.r.srem(r._metric_slugs_key, *keys)  # Remove the old keys
            r.r.sadd(r._metric_slugs_key, *slugs)  # Keep the new slugs

            p = "\nMetrics: Converted {0} Keys to {1} Slugs\n"
            self.stdout.write(p.format(len(keys), len(slugs)))
        except (IndexError, ResponseError):
            # If none of our old keys contain a ':', we don't need to replace them.
            pass

        # Similar to metric keys above...
        # Store *only* slugs in the Set of Gauge slugs. Prior to this, we
        # stored gauge keys, and split the slug from the key upon retrieval
        try:
            keys = r.r.smembers(r._gauge_slugs_key)
            slugs = set(s.split(":")[1] for s in keys)
            r.r.srem(r._gauge_slugs_key, *keys)  # Remove the old keys
            r.r.sadd(r._gauge_slugs_key, *slugs)  # Keep the new slugs

            p = "Gauges: Converted {0} Keys to {1} Slugs\n"
            self.stdout.write(p.format(len(keys), len(slugs)))
        except (IndexError, ResponseError):
            # If none of our old keys contain a ':', we don't need to replace them.
            pass

        # Convert all Categories from JSON to Sets.
        i = 0
        categories = r.categories()
        for category in categories:
            try:
                k = r._category_key(category)
                data = r.r.get(k)  # Get the JSON-ecoded list of metrics in this Category
                if data:  # redis gives us a None-value for a non-existing key
                    data = json.loads(data)  # convert to python
                    r.r.delete(k)  # Delete the existing info in redis
                    r.r.sadd(k, *set(data))  # Re-create as a Set
                    i += 1
            except ResponseError:
                pass

        if i > 0:
            p = "Converted {0} Categories from JSON -> Redis Sets\n"
            self.stdout.write(p.format(i))
