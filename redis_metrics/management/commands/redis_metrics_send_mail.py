from datetime import date

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import NoArgsCommand
from django.template.loader import render_to_string

from redis_metrics.models import R


class Command(NoArgsCommand):
    help = "Send Metrics Report E-mails"
    can_import_settings = True

    def handle_noargs(self, **options):
        """Send Report E-mails."""

        r = R()
        slugs = r.slugs()

        template = "redis_metrics/email/report.{fmt}"
        data = {
            'date': date.today(),
            'metrics': r.get_metrics(slugs)
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
