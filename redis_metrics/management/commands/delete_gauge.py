from django.core.management.base import BaseCommand, CommandError
from redis_metrics.models import R


class Command(BaseCommand):
    args = '<gauge-key>'
    help = "Removes a Gauge and its data"

    def handle(self, *args, **options):
        if not len(args) == 1:
            raise CommandError("You must provide a gauge name")
        r = R()
        r.delete_gauge(args[0])
