History
-------

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
