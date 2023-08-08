Usage
=====

Use the ``metric`` shortcut to start recording metrics.

::

    from redis_metrics import metric

    # Increment the metric by one
    metric('new-user-signup')

    # Increment the metric by some other number
    metric('new-user-signup', 4)


Metrics can also be categorized. To record a metric and add it to a category,
specify a ``category`` keyword parameter

::

    # Increment the metric, and add it to a category
    metric('new-user-signup', category="User Metrics")

Metrics can also expire after a specified number of seconds

::

    # The 'foo' metric will expire in 5 minutes
    metric('foo', expire=300)


You can also *reset* a metric with the ``set_metric`` function. This will
replace any existing values for the metric, rather than incrementing them. It's
api is similar to ``metric``'s.

::

    from redis_metrics import set_metric

    # Reset the Download count.
    set_metric("downloads", 0)


Gauges
------

There are also ``gauge``'s. A ``gauge`` is great for storing a *cumulative*
value, and when you don't care about keeping a history for the metric. In other
words, a gauge gives you a snapshot of some current value.

::

    from redis_metrics import gauge

    # Create a gauge
    gauge('total-downloads', 0)

    # Update the gauge
    gauge('total-downloads', 9999)


The R class
-----------

There's also an ``R`` class which is a lightweight wrapper around ``redis``.
You can use it directly to set metrics or gauges and to retrieve data.

::

    >>> from redis_metrics.models import R
    >>> r = R()
    >>> r.metric('new-user-signup')
    >>> r.get_metric('new-user-signup')
    {
        'second': 0,
        'minute': 0,
        'hour': 1,
        'day': '29',
        'month': '29',
        'week': '29',
        'year': '29'
    }

    # list the slugs you've used to create metrics
    >>> r.metric_slugs()
    set(['new-user-signup', 'user-logins'])

    # Get metrics for multiple slugs
    >>> r.get_metrics(['new-user-signup', 'user-logins'])
    [
        {'new-user-signup': {
            'second': '0', 'minute': '0', 'hour': '1',
            'day': '7', 'month': '7', 'week': '7', 'year': '7'}},
        {'user-logins':
            'second': '0', 'minute': '0', 'hour': '1',
            'day': '7', 'month': '7', 'week': '7', 'year': '7'}},
    ]

    # Delete a metric
    >>> r.delete_metric("app-errors")


Templatetags
------------

The included templatetags are useful for visualizing your stored metrics.


Load the templatetags in your template::
``{% load redis_metric_tags %}``

Viewing your data is possible with the built-in views, but these all make use
of a number of templatetags to display metric data and history.

* ``metrics_since(slugs, years, link_type="detail", granularity=None)`` Renders
  a template with a menu to view a metric (or a list of metrics) for a given
  number of years. For example::

    {% metrics_since "downloads" 5 %}  {# downloads for the last 5 years #}

* ``gauge(slug, maximum=9000, size=200, coerce='float')``: Includes a donut
  chart for the specified gauge. The maximum represents the largest possible
  value for the gague, while the size is the size of the chart in pixels. The
  coerce parameter tells the template tag how to coerce numeric data. By default
  values are converted to floats, but you can include ``coerce='int'`` to force
  values to be listed as integers.::

    {% gauge "tasks-completed" 10 size=300 coerce='int' %}

* ``metric_list`` generates a list of all metrics.
* ``metric_detail(slug, with_data_table=False)`` displays a metric's current
  details. This tag will also generate a table of raw data if the ``with_data_table``
  option is True.
* ``metric_history(slug, granularity="daily", since=None, to=None, with_data_table=False)``
  displays a given metric's history. The ``granularity`` option defines the
  granularity displayed, ``since`` is a string or datetime object that specifies
  the date and/or time from which we start displaying data, the ``to`` argument
  indicates to date or time to which we display data, and ``with_data_table``
  controls wether or not raw data is displayed in a table. Examples::

    {# dainly signups since Jan 1, 2015 #}
    {% metric_history "signups" "daily" "2015-01-01" %}

    {# daily signups between Jan 1, 2015 & Jan, 1 2016 #}
    {% metric_history "signups" "daily" "2015-01-01" "2016-01-01" %}

    {# monthly signups for a given year #}
    {% metric_history "signups" "monthly" this_year %}


    {# monthly signups for a given year, including data  #}
    {% metric_history "signups" "monthly" this_year with_data_table=True %}

* ``aggregate_detail(slug_list, with_data_table=False)`` is much like ``metric_detail``,
  but displayes more than one metric on the chart. The ``slug_list`` parameter should
  be a list of metric slugs that you want to display.
* ``aggregate_history(slug_list, granularity="daily", since=None, with_data_table=False)``
  is similarly like ``metric_history``, but for multiple metrics on once chart.
  but displayes more than one metric on the chart. The ``slug_list`` parameter should
  be a list of metric slugs that you want to display.
