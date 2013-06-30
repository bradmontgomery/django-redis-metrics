from django.core.management.base import BaseCommand, CommandError
from redis_metrics.utils import generate_test_metrics


class Command(BaseCommand):
    args = '<metric-name> [<metric-name> ...]'
    help = "Creates Lots of Dummy Metrics"
    can_import_settings = True

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("You must provide at least one metric name")
        metric_names = args

        days = 365 * 3  # 3 years of data
        for m in metric_names:
            generate_test_metrics(m, num=days, randomize=True)
