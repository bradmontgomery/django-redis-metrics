.. django-redis-metrics documentation master file, created by
   sphinx-quickstart on Thu Nov 19 09:37:56 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to django-redis-metrics's documentation!
================================================


This app allows you do define various named metrics (such as 'New Users',
'Downloads', or 'Purchases'), record when they happen, and quickly and easily
view that information.

Each metric can be assigned to an arbitrary category or given an optional
expiration time. Granularity for metrics are saved daily, weekly, monthly, and
yearly by default, but this libary gives you the ability to store event data
down to the second, minute, and hour.

Here's a sneak peak at how it works::

    >>> from redis_metrics.utils import metric
    >>> metric("Downloads", category="User Metrics")

See the usage section for more examples.


Inspiration
-----------

This app was inspired by Frank Wiles ``django-app-metrics``. It offers a
similar feature set but:

* It is *only* backed by Redis
* Does not require Celery
* Does not include any Timing


License
-------

This code is distributed under the terms of the MIT license. See the project's
``LICENSE.txt`` file for the full content of the license.


Learn More
----------

.. toctree::
   :maxdepth: 2

   installation
   usage
   contributing


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

