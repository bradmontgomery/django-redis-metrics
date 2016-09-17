from __future__ import unicode_literals
from datetime import datetime, timedelta

from django import template
from redis_metrics.utils import get_r
from redis_metrics.settings import GRANULARITIES

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
def gauge(slug, maximum=9000, size=200, coerce='float'):
    """Include a Donut Chart for the specified Gauge.

    * ``slug`` -- the unique slug for the Gauge.
    * ``maximum`` -- The maximum value for the gauge (default is 9000)
    * ``size`` -- The size (in pixels) of the gauge (default is 200)
    * ``coerce`` -- type to which gauge values should be coerced. The default
      is float. Use ``{% gauge some_slug coerce='int' %}`` to coerce to integer

    """
    coerce_options = {'float': float, 'int': int, 'str': str}
    coerce = coerce_options.get(coerce, float)

    redis = get_r()
    value = coerce(redis.get_gauge(slug))
    if value < maximum and coerce == float:
        diff = round(maximum - value, 2)
    elif value < maximum:
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
    granularities = list(r._granularities())
    metrics = r.get_metric(slug)
    metrics_data = []
    for g in granularities:
        metrics_data.append((g, metrics[g]))

    return {
        'granularities': [g.title() for g in granularities],
        'slug': slug,
        'metrics': metrics_data,
        'with_data_table': with_data_table,
    }


@register.inclusion_tag("redis_metrics/_metric_history.html")
def metric_history(slug, granularity="daily", since=None, to=None,
                   with_data_table=False):
    """Template Tag to display a metric's history.

    * ``slug`` -- the metric's unique slug
    * ``granularity`` -- the granularity: daily, hourly, weekly, monthly, yearly
    * ``since`` -- a datetime object or a string string matching one of the
      following patterns: "YYYY-mm-dd" for a date or "YYYY-mm-dd HH:MM:SS" for
      a date & time.
    * ``to`` -- the date until which we start pulling metrics
    * ``with_data_table`` -- if True, prints the raw data in a table.

    """
    r = get_r()
    try:
        if since and len(since) == 10:  # yyyy-mm-dd
            since = datetime.strptime(since, "%Y-%m-%d")
        elif since and len(since) == 19:  # yyyy-mm-dd HH:MM:ss
            since = datetime.strptime(since, "%Y-%m-%d %H:%M:%S")

        if to and len(to) == 10:  # yyyy-mm-dd
            to = datetime.strptime(since, "%Y-%m-%d")
        elif to and len(to) == 19:  # yyyy-mm-dd HH:MM:ss
            to = datetime.strptime(to, "%Y-%m-%d %H:%M:%S")

    except (TypeError, ValueError):
        # assume we got a datetime object or leave since = None
        pass

    metric_history = r.get_metric_history(
        slugs=slug,
        since=since,
        to=to,
        granularity=granularity
    )

    return {
        'since': since,
        'to': to,
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
    metrics_data = []
    granularities = r._granularities()

    # XXX converting granularties into their key-name for metrics.
    keys = ['seconds', 'minutes', 'hours', 'day', 'week', 'month', 'year']
    key_mapping = {gran: key for gran, key in zip(GRANULARITIES, keys)}
    keys = [key_mapping[gran] for gran in granularities]

    # Our metrics data is of the form:
    #
    #   (slug, {time_period: value, ... }).
    #
    # Let's convert this to (slug, list_of_values) so that the list of
    # values is in the same order as the granularties
    for slug, data in r.get_metrics(slug_list):
        values = [data[t] for t in keys]
        metrics_data.append((slug, values))

    return {
        'chart_id': "metric-aggregate-{0}".format("-".join(slug_list)),
        'slugs': slug_list,
        'metrics': metrics_data,
        'with_data_table': with_data_table,
        'granularities': [g.title() for g in keys],
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

    return {
        'chart_id': "metric-aggregate-history-{0}".format("-".join(slugs)),
        'slugs': slugs,
        'since': since,
        'granularity': granularity,
        'metric_history': history,
        'with_data_table': with_data_table,
    }
