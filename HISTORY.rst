History
-------

0.8.2 (coming soon)
+++++++++++++++++++

- support for weekly stats starting on mondays (`PR #16 <https://github.com/bradmontgomery/django-redis-metrics/pull/36>`_)

0.8.1 (2014-10-18)
++++++++++++++++++

- Refactored the way we pull settings within the app, added ``settings.AppSettings`` to do this.
- Added new settings: ``REDIS_METRICS_MIN_GRANULARITY`` and ``REDIS_METRICS_MAX_GRANULARITY`` (`Issue #34 <https://github.com/bradmontgomery/django-redis-metrics/issues/34>`_)
- Dropping support for 1.5 (which just means I'm not testing against it)

0.8.0 (2014-07-15)
++++++++++++++++++

- Replaced Google Charts with Chart.js (`Issue #21 <https://github.com/bradmontgomery/django-redis-metrics/issues/21>`_)
- Added the ability to set a metric's value rather than increment it via the
  ``set_metric`` function (`Issue #20 <https://github.com/bradmontgomery/django-redis-metrics/issues/20>`_)
- Support for metrics at a granularity of Seconds, Minutes, and Hours, (`#24 <https://github.com/bradmontgomery/django-redis-metrics/pull/24>`_ and `#13 <https://github.com/bradmontgomery/django-redis-metrics/issues/13>`_, thanks @mvillarejo)
- Autodecode data from redis (`PR #18 <https://github.com/bradmontgomery/django-redis-metrics/pull/18>`_, thanks @jellonek)
- Changed ``utils.generate_test_metrics`` so it only generates metrics at the
  daily and above level.
- **Potential Breaking change**: Always store dates & times in UTC
- **Potential Breaking change**: Change the way we store Metric & Gauge Slugs:
  Store only the slugs, not the redis keys.
- Added a ``fix_redis_metrics_keys`` command to migrate data for previous versions.

0.7.2 (2014-06-22)
++++++++++++++++++

- Now Uses redis sets to store category slugs (thanks @remohammadi!)

0.7.1 (2013-11-17)
++++++++++++++++++

- Minor changes to support Django 1.6
- Replaced Django's ``SortedDict`` with ``collections.OrderedDict``

0.7.0 (2013-08-04)
++++++++++++++++++

- Support for Redis password, socket timeout, and connection pool parameters.
  Thanks @charles-vdulac!

0.6.0 (2013-07-09)
++++++++++++++++++

- Default templates are now less hideous.
- Separated list of gauges and metrics into separate views.
- Added template tags: ``metric_list``, ``metric_detail``, ``metric_history``,
  ``aggregate_detail``, ``aggregate_history``, and ``metrics_since``.
- Added a ``gauge`` template tag.
- Added methods & management commands to delete metrics & gauges
- Updated email templates for the ``redis_metrics_send_mail`` command.
- Added a ``system_metric`` managment command
- Added ability to expire a metric

0.5.1 (2013-05-18)
++++++++++++++++++

- added category parameter to the ``metric`` function :-/
- hooked up Travis-CI

0.5.0 (2013-05-18)
++++++++++++++++++

- Added Categorization for metrics
- Added a management command to generate random metrics (for testing)
- ``MetricHistoryView`` and ``AggregateHistoryView`` accept a ``since``
  querystring parameter to specify the date from which reports are generated.
- 100% Test coverage


0.4.0 (2013-03-07)
++++++++++++++++++

- *Backwards Incompatible Change*: Changed the underlying Redis key for weekly
  metrics. See `Issue #7 <https://github.com/bradmontgomery/django-redis-metrics/issues/7>`_
  for a description of this bug.
- Added a management command--``reset_weekly_metrics``--that allows you to change
  the keys for weekly metrics
- Minor changes to the default templates


0.3.0 (2013-03-05)
++++++++++++++++++

- Support for Django 1.5's configurable User Model (only used in tests)
- Lazily instantiate R in ``utils`` so installing this actually works.
- Fixed the ``redis_metrics_send_mail`` command (Issue #2)
- Improvements to default templates


0.2.0 (2013-01-10)
++++++++++++++++++

- Ability to view metrics in Aggregate. See the ``AggregateFormView``,
  ``AggregateDetailView``, and ``AggregateHistoryView``
- Metric history reported in a columnar format. See
  ``R.get_metric_history_as_columns``.
- New Template tag: ``metric_slug``


0.1.x (2012-12-24)
++++++++++++++++++

- Various Bug Fixes
- Initial Release
