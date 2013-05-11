from datetime import date
from django.core.management.base import NoArgsCommand
from redis_metrics.utils import generate_test_metrics


class Command(NoArgsCommand):
    help = "Creates Lots of Dummy Metrics"
    can_import_settings = True

    def handle_noargs(self, **options):
        metric_names = [
            'test-thingy',
            'test-flangey',
            'test-foobley',
            'test-blahblah',
        ]
        days = 365 * 3  # 3 years of data
        for m in metric_names:
            generate_test_metrics(m, num=days, randomize=True)
