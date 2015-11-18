from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from redis_metrics.utils import get_r


class Command(BaseCommand):
    args = '<gauge-key>'
    help = "Removes a Gauge and its data"

    def handle(self, *args, **options):
        if not len(args) == 1:
            raise CommandError("You must provide a gauge name")
        r = get_r()
        r.delete_gauge(args[0])
