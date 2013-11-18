from django.conf.urls import patterns, url
from .views import (
    AggregateHistoryView, AggregateDetailView, AggregateFormView,
    CategoryFormView, DefaultView, GaugesView, MetricDetailView,
    MetricHistoryView, MetricsListView,
)


urlpatterns = patterns('',
    url(
        r'^categorize/(?P<category_name>.*)/$',
        CategoryFormView.as_view(),
        name='redis_metrics_categorize'
    ),
    url(
        r'^categorize/$',
        CategoryFormView.as_view(),
        name='redis_metrics_categorize'
    ),
    url(
        r'^aggregate/(?P<slugs>.*)/(?P<granularity>.*)/$',
        AggregateHistoryView.as_view(),
        name='redis_metric_aggregate_history'
    ),
    url(
        r'^aggregate/(?P<slugs>.*)/$',
        AggregateDetailView.as_view(),
        name='redis_metric_aggregate_detail'
    ),
    url(
        r'^aggregate/$',
        AggregateFormView.as_view(),
        name='redis_metric_aggregate'
    ),
    url(
        r'^list/$',
        MetricsListView.as_view(),
        name='redis_metrics_list'
    ),
    url(
        r'^gauges/$',
        GaugesView.as_view(),
        name='redis_metrics_gauges'
    ),
    url(
        r'^(?P<slug>.*)/(?P<granularity>.*)/$',
        MetricHistoryView.as_view(),
        name='redis_metric_history'
    ),
    url(
        r'^(?P<slug>.*)/$',
        MetricDetailView.as_view(),
        name='redis_metric_detail'
    ),
    url(
        r'^$',
        DefaultView.as_view(),
        name='redis_metrics_default'
    ),
)
