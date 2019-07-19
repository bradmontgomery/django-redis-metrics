from __future__ import unicode_literals
from django.urls import re_path

from .views import (
    AggregateHistoryView, AggregateDetailView, AggregateFormView,
    CategoryFormView, DefaultView, GaugesView, MetricDetailView,
    MetricHistoryView, MetricsListView,
)


urlpatterns = [
    re_path(
        r'^categorize/(?P<category_name>.*)/$',
        CategoryFormView.as_view(),
        name='redis_metrics_categorize'
    ),
    re_path(
        r'^categorize/$',
        CategoryFormView.as_view(),
        name='redis_metrics_categorize'
    ),
    re_path(
        r'^aggregate/category/(?P<category>.*)/$',
        AggregateDetailView.as_view(),
        name='redis_metric_aggregate_detail_by_category'
    ),
    re_path(
        r'^aggregate/(?P<slugs>.*)/(?P<granularity>.*)/$',
        AggregateHistoryView.as_view(),
        name='redis_metric_aggregate_history'
    ),
    re_path(
        r'^aggregate/(?P<slugs>.*)/$',
        AggregateDetailView.as_view(),
        name='redis_metric_aggregate_detail'
    ),
    re_path(
        r'^aggregate/$',
        AggregateFormView.as_view(),
        name='redis_metric_aggregate'
    ),
    re_path(
        r'^list/$',
        MetricsListView.as_view(),
        name='redis_metrics_list'
    ),
    re_path(
        r'^gauges/$',
        GaugesView.as_view(),
        name='redis_metrics_gauges'
    ),
    re_path(
        r'^(?P<slug>.*)/(?P<granularity>.*)/$',
        MetricHistoryView.as_view(),
        name='redis_metric_history'
    ),
    re_path(
        r'^(?P<slug>.*)/$',
        MetricDetailView.as_view(),
        name='redis_metric_detail'
    ),
    re_path(
        r'^$',
        DefaultView.as_view(),
        name='redis_metrics_default'
    ),
]
