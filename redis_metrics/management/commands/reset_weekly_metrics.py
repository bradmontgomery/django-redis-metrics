from __future__ import unicode_literals
import re

from datetime import date
from django.core.management.base import BaseCommand, CommandError
from redis_metrics.utils import r


class Command(BaseCommand):
    """

    Updates the weekly metrics so they use the new key format. For
    more information, see Issue #7: http://bit.ly/YEjtF9

    Essentially, weekly-aggregated metrics had a key of the form:

        m:<slug>:w:<nn>

    Where ``nn`` was the week number in the range: [00-52). They now take the
    form:

        m:<slug>:w:<yyyy-nn>

    Where ``yyyy`` is a 4-digit year, and ``nn`` is the week number.

    """
    args = '[year]'
    help = "Updates weekly metrics so they match the new key format"

    def handle(self, *args, **options):
        if len(args) == 0:
            # Use the current year
            year = date.today().year
        elif len(args) == 1:
            year = int(args[0])
        else:
            raise CommandError("Invalid arguments. Provide a 4-digit year.")

        r = R()

        # Retrieve all the metric keys of the form: "m:<slug>:w:<nn>"
        weekly_keys = filter(
            lambda k: re.match(r'^m:.+:w:\d\d', k) is not None,
            r.r.smembers(r._metric_slugs_key)
        )
        for old_key in weekly_keys:
            # Match   -> m:<slug>:w:<nn>
            # Replace -> m:<slug>:w:<yyyy-nn>
            parts = old_key.split(":")
            parts[-1] = "{0}-{1}".format(year, parts[-1])
            new_key = ":".join(parts)

            # Copy old metric value into new metric
            r.r.set(new_key, r.r.get(old_key))

            # Track the new key
            r.r.sadd(r._metric_slugs_key, new_key)

            # Delete the old metric?
            r.r.delete(old_key)

        # Delete the set of keys for the old weekly metrics
        r.r.srem(r._metric_slugs_key, *weekly_keys)
