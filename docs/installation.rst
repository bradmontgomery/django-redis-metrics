Installation
============

To get started quickly:

1. Run ``pip install django-redis-metrics``.
2. Adding ``redis_metrics`` to your INSTALLED_APPS.
3. Include ``url(r'^metrics/', include('redis_metrics.urls'))`` in your URLConf.


Requirements
------------

This app works with Python 2 & 3 (tested on 2.7 and 3.5) and is tested with
Django 1.8 - 1.10. It also requires `redis-py`_. For support for older versions
of Django, see the `0.9.0 release <https://github.com/bradmontgomery/django-redis-metrics/releases/tag/0.9.0>`_.

If you'd like to run the tests, install the packages listed in
``requirements/test.txt``, which includes coverage and mock.

.. _`redis-py`: https://github.com/andymccurdy/redis-py


Additional Installation
-----------------------

To install the current version, run ``pip install django-redis-metrics``.

You can also install the development version with
``pip install -e git://github.com/bradmontgomery/django-redis-metrics.git#egg=redis_metrics-dev``

To use the built-in views, add ``redis_metrics`` to your ``INSTALLED_APPS``,
and include the following in your Root URLconf::

    url(r'^metrics/', include('redis_metrics.urls')),

Then, to view your metrics, visit the /metrics/ url, (i.e. run the development
server and go to http://127.0.0.1:8000/metrics/)



Settings
--------

Starting with version 1.0, this app contains a single setting, ``REDIS_METRICS``,
which includes a number of options, all wich have the following defaults::

    REDIS_METRICS = {
       'CONNECTION_CLASS': None,
       'HOST': 'localhost',
       'PORT': 6379,
       'DB':  0,
       'PASSWORD': None,
       'SOCKET_TIMEOUT': None,
       'SOCKET_CONNECTION_POOL': None,
       'MIN_GRANULARITY': 'daily',
       'MAX_GRANULARITY': 'yearly',
       'MONDAY_FIRST_DAY_OF_WEEK': False,
       'USE_ISO_WEEK_NUMBER': False,
    }

Formerly, each of these were separate settings with a ``REDIS_METRICS_`` prefix.

* ``CONNECTION_CLASS``: Optional name of a function which returns an instance of a Redis client.
    * If you are using `django-redis`_ for caching, for example, then you can set this to ``'django_redis.get_redis_connection'`` to automatically use whatever `django-redis`_ is using to get its Redis client instances (`django-redis`_ supports pluggable back ends for Redis).
    * This can also be used to enable the use of Redis clients that support Redis Sentinel (e.g. use `django-redis-sentinel`_ along with `django-redis`_), Redis Clustering or Hiredis, for example.
    * You can also create your own class/function that returns a valid Redis client.
    * **Note that if you specify this setting, then all other Redis-related settings will be ignored** (namely ``HOST``, ``PORT``, ``DB``, ``PASSWORD``, ``SOCKET_TIMEOUT`` and ``SOCKET_CONNECTION_POOL``).
* ``HOST``: Hostname of redis server that will contain your metrics data; defaults to 'localhost'
* ``PORT``: Port of your redis server; defaults to '6379'
* ``DB``: Your redis database number to use, defaults to 0
* ``PASSWORD``: Your redis password if needed; defaults to None
* ``SOCKET_TIMEOUT``: Your redis database socket timeout; defaults to None
* ``SOCKET_CONNECTION_POOL``: Your redis database socket connection pool; defaults to None
* ``MIN_GRANULARITY``: The minimum-time granularity for your metrics; default is 'daily'.
* ``MAX_GRANULARITY``: The maximum-time granularity for your metrics; default is 'yearly'
* ``MONDAY_FIRST_DAY_OF_WEEK``: Set to True if week should start on Monday; default is False
* ``USE_ISO_WEEK_NUMBER``: Set to True to use ISO calendar weeks (see: https://docs.python.org/2/library/datetime.html#datetime.date.isocalendar)

.. _`django-redis`: https://github.com/niwinz/django-redis
.. _`django-redis-sentinel`: https://github.com/KabbageInc/django-redis-sentinel

Upgrading versions prior to 0.8.x
---------------------------------

If you used a version of this app prior to 0.8.0, it's likely that
you'll run into this error::

    WRONGTYPE Operation against a key holding the wrong kind of value

To fix this, run the ``fix_redis_metrics_keys`` command, which should migrate
data for metrics, gauges, and categories into the format used by the current
version of the app.
