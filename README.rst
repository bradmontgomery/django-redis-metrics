Django Redis Metrics
====================

This app is inspired by Frank Wiles' ``django-app-metrics``. It allows you to
define various named metrics (such as 'New User Signups', 'Downloads') and
record when they happen.

This app, however, is essentially stripped of all but the bare-bones features
offered by the Redis backend in ``django-app-metrics``. Major differences are:

* *only* backed by Redis
* does not require Celery
* currently no grouping of Metrics
* no timing

*TODO* In addition, there are some built-in default views and templates for viewing
metrics.


Requirements
============

The only requirement for this app is `redis-py`_ and Django 1.4 or above.

.. _`redis-py`: https://github.com/andymccurdy/redis-py


Installation
============

*TODO*: eventually, ``pip install django-redis-metrics``.

To use the (nascent) built-in views, add ``redis_metrics`` to your ``INSTALLED_APPS``.


Settings
========

``REDIS_METRICS_HOST`` - Hostname of redis server, defaults to 'localhost'

``REDIS_METRICS_PORT`` - redis port, defaults to '6379'

``REDIS_METRICS_DB`` - redis database number to use, defaults to 0


Usage
=====

Use the ``metric`` shortcut to start recording metrics.

::

  from redis_metrics import metric

  # Increment the metric by one
  metric('new-user-signup')

  # Increment the metric by some other number
  metric('new-user-signup', 4)

There are also ``gague``'s.

::

  from redis_metrics import gague

  # Create a gague
  gague('total-downloads', 0)

  # Update the gague
  gague('total-downloads', 9999)
