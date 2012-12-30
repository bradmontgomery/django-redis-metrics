Django Redis Metrics
====================

This app is inspired by Frank Wiles' ``django-app-metrics``. It allows you to
define various named metrics (such as 'New User Signups', 'Downloads') and
record when they happen.

However, this app is stripped of all but the bare-bones features offered by the
Redis backend in ``django-app-metrics``. Major differences are:

* *only* backed by Redis
* does not require Celery
* currently no grouping of Metrics
* no timing

In addition, there are some built-in default views and templates for viewing
metrics and charts backed by google charts.


License
=======

This code is distributed under the terms of the MIT license. See the
``LICENSE.txt`` file.


Requirements
============

The only requirement for this app is `redis-py`_ and Django 1.4 or above.

.. _`redis-py`: https://github.com/andymccurdy/redis-py


Installation
============

This app is not yet *pip-install-able*. (See *TODO*). You can do one of the
following to start using it, though:

* ``pip install`` the development version:
  ``pip install -e git://github.com/bradmontgomery/django-redis-metrics.git#egg=redis_metrics-dev``
* Clone this repo and add the ``redis_metrics`` directory on your python path
  (e.g. copy it into your Django project directory)

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


Usage
=====

Use the ``metric`` shortcut to start recording metrics.

::

    from redis_metrics import metric

    # Increment the metric by one
    metric('new-user-signup')

    # Increment the metric by some other number
    metric('new-user-signup', 4)

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


Todo
====

* Better Test Coverage.
* Add a proper ``setup.py`` and host at PyPi so this can be installed with
  ``pip install django-redis-metrics``.
