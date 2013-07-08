from datetime import datetime, timedelta

from django import template
from redis_metrics.models import R

register = template.Library()


@register.inclusion_tag("redis_metrics/_since.html")
def metrics_since(slugs, years, link_type="detail", granularity=None):
    """Renders a template with a menu to view a metric (or metrics) for a
    given number of years.

    * ``slugs`` -- A Slug or a set/list of slugs
    * ``years`` -- Number of years to show past metrics
    * ``link_type`` -- What type of chart do we want ("history" or "aggregate")
        * history  -- use when displaying a single metric's history
        * aggregate -- use when displaying aggregate metric history
    * ``granularity`` -- For "history" only; show the metric's granularity;
      default is "daily"

    """
    # Determine if we're looking at one slug or multiple slugs
    if type(slugs) in [list, set]:
        slugs = "+".join(s.lower().strip() for s in slugs)

    # Set the default granularity if it's omitted
    granularity = granularity.lower().strip() if granularity else "daily"

    # Build the parameters passed to the `url` template tag
    slug_values = []  # Each item is: (slug, since, num_years, granularity)
    for y in range(1, years + 1):
        slug_values.append(
            (slugs, datetime.today() - timedelta(days=365 * y), y, granularity)
        )
    return {'slug_values': slug_values, 'link_type': link_type.lower().strip()}


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


@register.inclusion_tag("redis_metrics/_metric_history.html")
def metric_history(slug, granularity="daily", since=None):
    """Template Tag to display a metric's history.

    * ``slug`` -- the metric's unique slug
    * ``granularity`` -- the granularity: daily, weekly, monthly, yearly
    * ``since`` -- a date string of the form "YYYY-mm-dd";

    """
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d")
    except (TypeError, ValueError):
        since_date = None

    metric_history = R().get_metric_history(
        slugs=slug,
        since=since_date,
        granularity=granularity
    )

    return {
        'slug': slug,
        'granularity': granularity,
        'metric_history': metric_history,
    }


@register.inclusion_tag("redis_metrics/_aggregate_detail.html")
def aggregate_detail(slug_list):
    """Template Tag to display multiple metrics.

    * ``slug_list`` -- A list of slugs to display

    """
    return {
        'slugs': slug_list,
        'metrics': R().get_metrics(slug_list)
    }


@register.inclusion_tag("redis_metrics/_aggregate_history.html")
def aggregate_history(slugs, granularity="daily", since=None):
    """Template Tag to display history for multiple metrics.

    * ``slug_list`` -- A list of slugs to display
    * ``granularity`` -- the granularity: daily, weekly, monthly, yearly
    * ``since`` -- a date string of the form "YYYY-mm-dd";

    """
    slugs = list(slugs)
    try:
        since_date = datetime.strptime(since, "%Y-%m-%d")
    except (TypeError, ValueError):
        since_date = None

    metric_history = R().get_metric_history_as_columns(
        slugs=slugs,
        since=since_date,
        granularity=granularity
    )

    return {
        'slugs': slugs,
        'granularity': granularity,
        'metric_history': metric_history,
    }
