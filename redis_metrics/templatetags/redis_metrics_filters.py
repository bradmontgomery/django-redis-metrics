from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(name="int")
@stringfilter
def to_int(value):
    """Converts the given string value into an integer. Returns 0 if the
    conversion fails."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


@register.filter(name='strip_metric_prefix')
@stringfilter
def strip_metric_prefix(value):
    """Strips the "m:<slug>" prefix from a metric.
    Applying this filter to the keys for each metric will have the following
    results:

    * Seconds -- from: ``m:<slug>:s:<yyyy-mm-dd-hh-MM-SS>`` to ``<yyyy-mm-dd-hh-MM-SS>``
    * Minutes -- from: ``m:<slug>:i:<yyyy-mm-dd-hh-MM>`` to ``<yyyy-mm-dd-hh-MM>``
    * Hourly -- from: ``m:<slug>:h:<yyyy-mm-dd-hh>`` to ``<yyyy-mm-dd-hh>``
    * Daily -- from: ``m:<slug>:<yyyy-mm-dd>`` to ``<yyyy-mm-dd>``
    * Weekly -- from ``m:<slug>:w:<num>`` to ``w:<num>``
    * Monthly -- from ``m:<slug>:m:<yyyy-mm>`` to ``m:<yyyy-mm>``
    * Yearly -- from ``m:<slug>:y:<yyyy>`` to ``y:<yyyy>``

    """
    return ':'.join(value.split(":")[2:])


@register.filter(name='metric_slug')
@stringfilter
def metric_slug(value):
    """Given a redis key value for a metric, returns only the slug.
    Applying this filter to the keys for each metric will have the following
    results:

    * Converts ``m:foo:s:<yyyy-mm-dd-hh-MM-SS>`` to ``foo``
    * Converts ``m:foo:i:<yyyy-mm-dd-hh-MM>`` to ``foo``
    * Converts ``m:foo:h:<yyyy-mm-dd-hh>`` to ``foo``
    * Converts ``m:foo:<yyyy-mm-dd>`` to ``foo``
    * Converts ``m:foo:w:<num>`` to ``foo``
    * Converts ``m:foo:m:<yyyy-mm>`` to ``foo``
    * Converts ``m:foo:y:<yyyy>`` to ``foo``

    """
    return value.split(":")[1]
