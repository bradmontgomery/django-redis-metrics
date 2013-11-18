History
-------

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
