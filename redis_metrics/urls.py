from django.conf.urls.defaults import patterns, url
from .views import (AggregateHistoryView, AggregateDetailView,
                    AggregateFormView, MetricDetailView,
                    MetricHistoryView, MetricsListView)


urlpatterns = patterns('',
    url(r'^aggregate/(?P<slugs>.*)/(?P<granularity>.*)/$',
        AggregateHistoryView.as_view(),
        name='redis_metric_aggregate_history'),
    url(r'^aggregate/(?P<slugs>.*)/$',
        AggregateDetailView.as_view(),
        name='redis_metric_aggregate_detail'),
    url(r'^aggregate/$',
        AggregateFormView.as_view(),
        name='redis_metric_aggregate'),
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
