"""
Views to display Metric data.

Note on Implementation: Since this app doesn't really use django's Models,
the views here are extended from ``TemplateView`` in order to keep things
simple.

"""
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from .models import R


class ProtectedTemplateView(TemplateView):
    """Ensures that Users are authenticated and that they're staff users. This
    is used as a parent class for the rest of the views in this app."""

    _logged_in_staff = lambda u: u.is_authenticated() and u.is_staff

    @method_decorator(user_passes_test(_logged_in_staff))
    def dispatch(self, *args, **kwargs):
        return super(ProtectedTemplateView, self).dispatch(*args, **kwargs)


class MetricsListView(ProtectedTemplateView):
    template_name = "redis_metrics/metrics_list.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(MetricsListView, self).get_context_data(**kwargs)
        r = R()
        data['metric_slugs'] = r.metric_slugs()

        # Include gauges in the default View. They're *technically* a list
        # of metrics, too!
        gauges = {
            'slugs': list(r.gauge_slugs()),
            'data': {}
        }
        if gauges['slugs']:
            for slug in gauges['slugs']:
                gauges['data'][slug] = r.get_gauge(slug)
        data['gauges'] = gauges
        return data


class MetricDetailView(ProtectedTemplateView):
    template_name = "redis_metrics/metric_detail.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(MetricDetailView, self).get_context_data(**kwargs)
        data['slug'] = kwargs['slug']
        data['metrics'] = R().get_metric(kwargs['slug'])
        return data


class MetricHistoryView(ProtectedTemplateView):
    template_name = "redis_metrics/metric_history.html"

    def get_context_data(self, **kwargs):
        """Includes the metrics slugs in the context."""
        data = super(MetricHistoryView, self).get_context_data(**kwargs)
        try:
            data.update({
                'slug': kwargs['slug'],
                'granularity': kwargs['granularity'],
                'metric_history': R().get_metric_history(
                    slug=kwargs['slug'],
                    granularity=kwargs['granularity']
                )
            })
        except KeyError:
            raise Http404
        return data
