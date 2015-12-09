from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from redis_metrics.utils import get_r


class Command(BaseCommand):
    args = '<metric-key>'
    help = "Removes a metric and its data"

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("You must provide a metric name")
        metric_slug = args[0]

        r = get_r()
        r.delete_metric(metric_slug)
