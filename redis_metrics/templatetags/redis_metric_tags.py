from django import template
from redis_metrics.models import R

register = template.Library()


@register.inclusion_tag("redis_metrics/_gauge.html")
def gauge(slug, maximum=9000, size=125):
    r = R()
    return {
        'slug': slug,
        'current_value': r.get_gauge(slug),
        'max_value': maximum,
        'size': size,
        'yellow': maximum - (maximum / 2),
        'red': maximum - (maximum / 4),
    }


@register.inclusion_tag("redis_metrics/_metric_list.html")
def metric_list():
    return {
        'metrics': R().metric_slugs_by_category(),
    }


@register.inclusion_tag("redis_metrics/_metric_detail.html")
def metric_detail(slug):
    return {
        'slug': slug,
        'metrics': R().get_metric(slug),
    }
