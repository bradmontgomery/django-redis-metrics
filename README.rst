Django Redis Metrics
====================

.. image:: https://secure.travis-ci.org/bradmontgomery/django-redis-metrics.png
    :alt: Build Status
    :target: http://travis-ci.org/bradmontgomery/django-redis-metrics

.. image:: https://pypip.in/d/django-redis-metrics/badge.png
        :target: https://crate.io/packages/django-redis-metrics/


This app allows you do define various named metrics (such as 'New Users',
'Downloads', or 'Purchases') and record when they happen.

Eat metric can be assigned a Category or an optional Expiration time, and is
stored at the second, minute, hourly, daily, weekly, monthly, and yearly level,
so you can see the frequency of your data at different granularities.

Here's a sneak peak at how it works::

    >>> from redis_metrics.utils import metric
    >>> metric("Downloads", category="User Metrics")

See the usage_ section for more examples.

Inspiration
-----------

This app was inspired by Frank Wiles ``django-app-metrics``. It offers a
similar feature set but:

* It is *only* backed by Redis
* Does not require Celery
* Does not include any Timing


Requirements
------------

This app works with Python 2.7 and Django 1.4 - 1.6 and requires `redis-py`_.

If you'd like to run the tests, install the packages listed in
``requirements/test.txt``, which includes coverage and mock.

.. _`redis-py`: https://github.com/andymccurdy/redis-py


Installation
------------

To install the current version, run ``pip install django-redis-metrics``.

You can also install the development version with
``pip install -e git://github.com/bradmontgomery/django-redis-metrics.git#egg=redis_metrics-dev``

To use the built-in views, add ``redis_metrics`` to your ``INSTALLED_APPS``,
and include the following in your Root URLconf::

    url(r'^metrics/', include('redis_metrics.urls')),

Then, to view your metrics, visit the /metrics/ url, (i.e. run the development
server and go to http://127.0.0.1:8000/metrics/)


Upgrading to 0.8.0
------------------

If you used a prior version of this app, then installed 0.8.0, it's likely that
you'll run into this error::

    WRONGTYPE Operation against a key holding the wrong kind of value

To fix this, run the ``fix_redis_metrics_keys`` command, which should mitgrate
data for metrics, gauges, and categories.


Settings
--------

* ``REDIS_METRICS_HOST`` - Hostname of redis server, defaults to 'localhost'
* ``REDIS_METRICS_PORT`` - redis port, defaults to '6379'
* ``REDIS_METRICS_DB`` - redis database number to use, defaults to 0
* ``REDIS_METRICS_PASSWORD`` - redis database password to use, defaults to None
* ``REDIS_METRICS_SOCKET_TIMEOUT`` - redis database socket timeout, defaults to None
* ``REDIS_METRICS_SOCKET_CONNECTION_POOL`` - redis database socket connection
  pool, defaults to None

.. _usage:

Usage
-----

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


There are also ``gauge``'s. A ``gauge`` is great for storing a *cumulative*
value, and when you don't care about keeping a history for the metric.

::

    from redis_metrics import gauge

    # Create a gauge
    gauge('total-downloads', 0)

    # Update the gauge
    gauge('total-downloads', 9999)


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


Contributing
------------

Feel free to submit bug reports or pull requests on `the github repo`_.

If you do submit a pull request, please consider running the tests and (if
applicable) adding test coverage for your changes. Thank You!

.. _`the github repo`: https://github.com/bradmontgomery/django-redis-metrics


License
-------

This code is distributed under the terms of the MIT license. See the
``LICENSE.txt`` file.
