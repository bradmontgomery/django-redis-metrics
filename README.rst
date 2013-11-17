Django Redis Metrics
====================

.. image:: https://secure.travis-ci.org/bradmontgomery/django-redis-metrics.png
    :alt: Build Status
    :target: http://travis-ci.org/bradmontgomery/django-redis-metrics

.. image:: https://pypip.in/d/django-redis-metrics/badge.png
        :target: https://crate.io/packages/django-redis-metrics/

This app is inspired by Frank Wiles ``django-app-metrics``. It allows you to
define various named metrics (such as 'New User Signups', 'Downloads') and
record when they happen.

However, this app is stripped of all but the bare-bones features offered by the
Redis backend in ``django-app-metrics``. Major differences are:

* *only* backed by Redis
* does not require Celery
* no timing

Additionally, there are some built-in views and templates that include charts
(backed by the Google Charts API) for metrics.


License
=======

This code is distributed under the terms of the MIT license. See the
``LICENSE.txt`` file.


Requirements
============

This app works with Django 1.4, 1.5, and 1.6 and only requires `redis-py`_.

If you'd like to run the tests, install the packages listed in
``requirements/test.txt``.

.. _`redis-py`: https://github.com/andymccurdy/redis-py


Installation
============

To install the current version, run ``pip install django-redis-metrics``.

You can also install the development version with
``pip install -e git://github.com/bradmontgomery/django-redis-metrics.git#egg=redis_metrics-dev``

To use the built-in views, add ``redis_metrics`` to your ``INSTALLED_APPS``,
and include the following in your Root URLconf::

    url(r'^metrics/', include('redis_metrics.urls')),

Then, to view your metrics, visit the /metrics/ url, (i.e. run the development
server and go to http://127.0.0.1:8000/metrics/)


Settings
========

* ``REDIS_METRICS_HOST`` - Hostname of redis server, defaults to 'localhost'
* ``REDIS_METRICS_PORT`` - redis port, defaults to '6379'
* ``REDIS_METRICS_DB`` - redis database number to use, defaults to 0
* ``REDIS_METRICS_PASSWORD`` - redis database password to use, defaults to None
* ``REDIS_METRICS_SOCKET_TIMEOUT`` - redis database socket timeout, defaults to None
* ``REDIS_METRICS_SOCKET_CONNECTION_POOL`` - redis database socket connection pool, defaults to None


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

There are also ``gauge``'s.

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
    {'day': '29', 'month': '29', 'week': '29', 'year': '29'}

    # list the slugs you've used to create metrics
    >>> r.metric_slugs()
    set(['new-user-signup', 'user-logins'])

    # Get metrics for multiple slugs
    >>> r.get_metrics(['new-user-signup', 'user-logins'])
    [
        {'new-user-signup':
            {'day': '7', 'month': '7', 'week': '7', 'year': '7'}},
        {'user-logins':
            {'day': '29', 'month': '29', 'week': '29', 'year': '29'}}
    ]


Contributing
============

Feel free to submit bug reports or pull requests on `the github repo`_.

.. _`the github repo`: https://github.com/bradmontgomery/django-redis-metrics
