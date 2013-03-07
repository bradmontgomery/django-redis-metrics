History
-------

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
