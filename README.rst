Django Redis Metrics
====================

|docs| |version| |coveralls| |license|


This app allows you do define various named metrics (such as 'New Users',
'Downloads', or 'Purchases') and record when they happen.

Each metric can be assigned a Category or an optional Expiration time, and is
stored at the second, minute, hourly, daily, weekly, monthly, and yearly level,
so you can see the frequency of your data at different granularities.

Here's a sneak peak at how it works::

    >>> from redis_metrics.utils import metric
    >>> metric("Downloads", category="User Metrics")


Compatibility
-------------

This app works with Python 3 and is tested with Django 2.2. For support for
older versions of Django, see the
`1.7.0 release <https://github.com/bradmontgomery/django-redis-metrics/releases/tag/v1.7.0>`_.


Documentation
-------------

View the full documenation at http://django-redis-metrics.readthedocs.io/en/latest/.

License
-------

This code is distributed under the terms of the MIT license. See the
``LICENSE.txt`` file.


.. |version| image:: http://img.shields.io/pypi/v/django-redis-metrics.svg?style=flat-square
    :alt: Current Release
    :target: https://pypi.python.org/pypi/django-redis-metrics/

.. |coveralls| image:: http://img.shields.io/coveralls/bradmontgomery/django-redis-metrics/master.svg?style=flat-square
    :alt: Code Coverage
    :target: https://coveralls.io/r/bradmontgomery/django-redis-metrics

.. |license| image:: http://img.shields.io/pypi/l/django-redis-metrics.svg?style=flat-square
    :alt: License
    :target: https://pypi.python.org/pypi/django-redis-metrics/

.. |docs| image:: https://img.shields.io/badge/Docs-Latest-brightgreen.svg?style=flat-square
    :target: http://django-redis-metrics.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status
