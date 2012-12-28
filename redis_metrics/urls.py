from django.conf.urls.defaults import patterns, url
from .views import MetricDetailView, MetricHistoryView, MetricsListView


urlpatterns = patterns('',
    url(r'^(?P<slug>.*)/(?P<granularity>.*)/$',
        MetricHistoryView.as_view(),
        name='redis_metric_history'),
    url(r'^(?P<slug>.*)/$',
        MetricDetailView.as_view(),
        name='redis_metric_detail'),
    url(r'^$',
        MetricsListView.as_view(),
        name='redis_metrics_list'),
)
