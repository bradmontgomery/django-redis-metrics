from __future__ import unicode_literals
from datetime import datetime, timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string

from redis_metrics.utils import get_r


class Command(NoArgsCommand):
    help = "Send Metrics Report E-mails"
    can_import_settings = True

    def handle_noargs(self, **options):
        """Send Report E-mails."""

        r = get_r()
        since = datetime.utcnow() - timedelta(days=1)
        metrics = {}
        categories = r.metric_slugs_by_category()
        for category_name, slug_list in categories.items():
            metrics[category_name] = []
            for slug in slug_list:
                metric_values = r.get_metric_history(slug, since=since)
                metrics[category_name].append(
                    (slug, metric_values)
                )

        # metrics is now:
        # --------------
        # { Category : [
        #     ('foo', [('m:foo:2012-07-18', 1), ('m:foo:2012-07-19, 2), ...])
        #   ],
        #   ...
        # }

        template = "redis_metrics/email/report.{fmt}"
        data = {
            'today': since,
            'metrics': metrics,
        }

        message = render_to_string(template.format(fmt='txt'), data)
        message_html = render_to_string(template.format(fmt='html'), data)
        msg = EmailMultiAlternatives(
            subject="Redis Metrics Report",
            body=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[email for name, email in settings.ADMINS]
        )
        msg.attach_alternative(message_html, "text/html")
        msg.send()
