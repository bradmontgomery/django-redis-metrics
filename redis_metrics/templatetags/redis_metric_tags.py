from __future__ import unicode_literals
from datetime import datetime, timedelta

from django import template
from redis_metrics.utils import get_r

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
    now = datetime.utcnow()

    # Determine if we're looking at one slug or multiple slugs
    if type(slugs) in [list, set]:
        slugs = "+".join(s.lower().strip() for s in slugs)

    # Set the default granularity if it's omitted
    granularity = granularity.lower().strip() if granularity else "daily"

    # Each item is: (slug, since, text, granularity)
    # Always include values for Today, 1 week, 30 days, 60 days, 90 days...
    slug_values = [
        (slugs, now - timedelta(days=1), "Today", granularity),
        (slugs, now - timedelta(days=7), "1 Week", granularity),
        (slugs, now - timedelta(days=30), "30 Days", granularity),
        (slugs, now - timedelta(days=60), "60 Days", granularity),
        (slugs, now - timedelta(days=90), "90 Days", granularity),
    ]

    # Then an additional number of years
    for y in range(1, years + 1):
        t = now - timedelta(days=365 * y)
        text = "{0} Years".format(y)
        slug_values.append((slugs, t, text, granularity))
    return {'slug_values': slug_values, 'link_type': link_type.lower().strip()}


@register.inclusion_tag("redis_metrics/_gauge.html")
def gauge(slug, maximum=9000, size=200):
    """Include a Donut Chart for the specified Gauge.

    * ``slug`` -- the unique slug for the Gauge.
    * ``maximum`` -- The maximum value for the gauge (default is 9000)
    * ``size`` -- The size (in pixels) of the gauge (default is 200)

    """
    r = get_r()
    value = int(r.get_gauge(slug))
    if value < maximum:
        diff = maximum - value
    else:
        diff = 0

    return {
        'slug': slug,
        'current_value': value,
        'max_value': maximum,
        'size': size,
        'diff': diff,
    }


@register.inclusion_tag("redis_metrics/_metric_list.html")
def metric_list():
    r = get_r()
    return {
        'metrics': r.metric_slugs_by_category(),
    }


@register.inclusion_tag("redis_metrics/_metric_detail.html")
def metric_detail(slug, with_data_table=False):
    """Template Tag to display a metric's *current* detail.

    * ``slug`` -- the metric's unique slug
    * ``with_data_table`` -- if True, prints the raw data in a table.

    """
    r = get_r()
    return {
        'granularities': list(r._granularities()),
        'slug': slug,
        'metrics': r.get_metric(slug),
        'with_data_table': with_data_table,
    }


@register.inclusion_tag("redis_metrics/_metric_history.html")
def metric_history(slug, granularity="daily", since=None, with_data_table=False):
    """Template Tag to display a metric's history.

    * ``slug`` -- the metric's unique slug
    * ``granularity`` -- the granularity: daily, hourly, weekly, monthly, yearly
    * ``since`` -- a datetime object or a string string matching one of the
      following patterns: "YYYY-mm-dd" for a date or "YYYY-mm-dd HH:MM:SS" for
      a date & time.
    * ``with_data_table`` -- if True, prints the raw data in a table.

    """
    r = get_r()
    try:
        if since and len(since) == 10:  # yyyy-mm-dd
            since = datetime.strptime(since, "%Y-%m-%d")
        elif since and len(since) == 19:  # yyyy-mm-dd HH:MM:ss
            since = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        # assume we got a datetime object or leave since = None
        pass

    metric_history = r.get_metric_history(
        slugs=slug,
        since=since,
        granularity=granularity
    )

    return {
        'since': since,
        'slug': slug,
        'granularity': granularity,
        'metric_history': metric_history,
        'with_data_table': with_data_table,
    }


@register.inclusion_tag("redis_metrics/_aggregate_detail.html")
def aggregate_detail(slug_list, with_data_table=False):
    """Template Tag to display multiple metrics.

    * ``slug_list`` -- A list of slugs to display
    * ``with_data_table`` -- if True, prints the raw data in a table.

    """
    r = get_r()
    return {
        'chart_id': "metric-aggregate-{0}".format("-".join(slug_list)),
        'slugs': slug_list,
        'metrics': r.get_metrics(slug_list),
        'with_data_table': with_data_table,
    }


@register.inclusion_tag("redis_metrics/_aggregate_history.html")
def aggregate_history(slugs, granularity="daily", since=None, with_data_table=False):
    """Template Tag to display history for multiple metrics.

    * ``slug_list`` -- A list of slugs to display
    * ``granularity`` -- the granularity: seconds, minutes, hourly,
                         daily, weekly, monthly, yearly
    * ``since`` -- a datetime object or a string string matching one of the
      following patterns: "YYYY-mm-dd" for a date or "YYYY-mm-dd HH:MM:SS" for
      a date & time.
    * ``with_data_table`` -- if True, prints the raw data in a table.

    NOTE: If you specify with_data_table=True, this code will make an additional
    call out to retreive metrics and format them properly, which could be a
    little slow.

    """
    r = get_r()
    slugs = list(slugs)

    try:
        if since and len(since) == 10:  # yyyy-mm-dd
            since = datetime.strptime(since, "%Y-%m-%d")
        elif since and len(since) == 19:  # yyyy-mm-dd HH:MM:ss
            since = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")
    except (TypeError, ValueError):
        # assume we got a datetime object or leave since = None
        pass

    history = r.get_metric_history_chart_data(
        slugs=slugs,
        since=since,
        granularity=granularity
    )
    # If we want to display the raw data, fetch it in a columnar format
    tabular_data = None
    if with_data_table:
        tabular_data = r.get_metric_history_as_columns(
            slugs=slugs,
            since=since,
            granularity=granularity
        )

    return {
        'chart_id': "metric-aggregate-history-{0}".format("-".join(slugs)),
        'slugs': slugs,
        'since': since,
        'granularity': granularity,
        'metric_history': history,
        'with_data_table': with_data_table,
        'tabular_data': tabular_data,
    }
