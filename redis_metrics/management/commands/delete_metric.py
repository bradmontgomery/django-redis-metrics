from django.core.management.base import BaseCommand, CommandError
from redis_metrics.models import R


class Command(BaseCommand):
    args = '<metric-key>'
    help = "Removes a metric and its data"

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("You must provide a metric name")
        metric_slug = args[0]

        r = R()
        r.delete_metric(metric_slug)
