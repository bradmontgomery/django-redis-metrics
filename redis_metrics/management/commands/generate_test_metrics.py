from __future__ import unicode_literals
from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from redis_metrics.utils import generate_test_metrics


class Command(BaseCommand):
    args = '<metric-name> [<metric-name> ...]'
    help = "Creates Lots of Dummy Metrics"
    option_list = BaseCommand.option_list + (
        make_option(
            '-r',
            '--randomize',
            action='store_true',
            dest='randomize',
            default=True,
            help='Randomize Metric Data'
        ),
        make_option(
            '--no-randomize',
            action='store_false',
            dest='randomize',
            default=True,
            help='Do not randomize Metric Data'
        ),
        make_option(
            '-n',
            '--num-days',
            action='store',
            dest='num_days',
            type="int",
            default=365 * 3,  # Default to 3 years
            help='Number of Days worth of data to generate'
        ),
        make_option(
            '-c',
            '--cap',
            action='store',
            dest='cap',
            default=None,
            help='Cap the maximum metric value'
        ),
    )

    def handle(self, *args, **options):
        if len(args) == 0:
            raise CommandError("You must provide at least one metric name")

        slugs = args
        cap = options["cap"]
        days = options["num_days"]
        randomize = options["randomize"]

        self.stdout.write("\nGenerating metrics using the following:\n")
        self.stdout.write("Slugs: {0}\n".format(u", ".join(slugs)))
        self.stdout.write("Days: {0}\n".format(days))
        self.stdout.write("Randomize: {0}\n".format(randomize))
        self.stdout.write("Cap: {0}\n".format(cap))

        for slug in slugs:
            generate_test_metrics(slug, num=days, randomize=randomize, cap=cap)
