History
-------

2.1.0 (2023-03-23)
++++++++++++++++++

- Updated to work with Django 3+
- Added pyproject.toml setup configuration.
- Removed travis setup
- Added pip-tools to manage requirements.

2.0.0 (2019-07-19)
++++++++++++++++++

- Dropped support for Python 2 (Python 3.6+ only)
- Support for Django 2.2. Thanks to `Derek Marsh <https://github.com/dmarsh19>`_ for
`PR #62 <https://github.com/bradmontgomery/django-redis-metrics/pull/62>_`.
- Updated Docs.


1.7.0 (2019-07-19)
++++++++++++++++++

- Added support for using ISO Week numbers. Thanks to `Elias Laitinen <https://github.com/eliasla>`_ for `PR #61 <https://github.com/bradmontgomery/django-redis-metrics/pull/61>_`)

1.6.0 (2017-02-06)
++++++++++++++++++

- Removed the bundled font-awesome files in favor of using the CDN-hosted version. (see `Issue #57 <https://github.com/bradmontgomery/django-redis-metrics/issues/57>`_ and `PR #58 <https://github.com/bradmontgomery/django-redis-metrics/pull/58>`_).


1.5.0 (2016-09-16)
++++++++++++++++++

- UI improvements for default templates (see `Issue #55 <https://github.com/bradmontgomery/django-redis-metrics/issues/55>`_.) including viewing aggregates per Category.
- Changed the formatting of `aggregate_detail` and `aggregate_history` template tags.
- Removed the returned `tabular_data` value from the `aggregate_history` template tag.
- Included inline styles for template tags so chart legends display correctly.
- Updated Bootstrap to 3.3.7
- Upgrade to Chart.js 2.2.2
- Added font-awesome.


1.4.0 (2016-04-25)
++++++++++++++++++

- Added support for a ``to`` argument in ``R.get_metric_history``, so you can
  specify a date range for metrics. (`PR #54 <https://github.com/bradmontgomery/django-redis-metrics/pull/54>`_, Thanks @stephanpoetschner).
- Updated the ``metric_history`` tag so that it also accepts a ``to`` argument.


1.3.0 (2016-04-01)
++++++++++++++++++

- Added a ``coerce`` parameter to the ``gauge`` template tag, and changed the
  default behavior so that guage values are listed at floats.
- Included a better default layout for gauges.
- Updating documentation.

1.2.0 (2016-03-31)
++++++++++++++++++

- Removed `{% load url from future %}` to be compatible with django 1.9 (`PR #52 <https://github.com/bradmontgomery/django-redis-metrics/pull/52>`_, thanks Phoebe Bright!)

1.1.0 (2015-12-13)
++++++++++++++++++

- This release introduces pluggable Redis backends. See `Issue #49 <https://github.com/bradmontgomery/django-redis-metrics/issues/49>`_ and `PR #50 <https://github.com/bradmontgomery/django-redis-metrics/pull/50>`_. Thanks Seamus Mac Conaonaigh!

1.0.3 (2015-11-20)
++++++++++++++++++

- Fixed regression resulting in duplicate metrics (`issue #48 <https://github.com/bradmontgomery/django-redis-metrics/issues/48>`_)

1.0.1/1.0.2 (2015-11-19)
++++++++++++++++++

- Fixed setup.py so all static files get distributed.
- And also fixed the Manifest.

1.0.0 (2015-11-19)
++++++++++++++++++

- Dropped support for Django versions prior to 1.7
- Support for Python 3 (`issue #28 <https://github.com/bradmontgomery/django-redis-metrics/issues/28>`_)
- Testing under Django 1.8 (`issue #39 <https://github.com/bradmontgomery/django-redis-metrics/issues/39>`_)
- Introduced the ``REDIS_METRICS`` settings (`issue #46 <https://github.com/bradmontgomery/django-redis-metrics/issues/46>`_)
- Bundled Bootstrap and revised the default templates (`issue #38 <https://github.com/bradmontgomery/django-redis-metrics/issues/38>`_)
- Created Proper docs for readthedocs.org (`issue #29 <https://github.com/bradmontgomery/django-redis-metrics/issues/29>`_)

0.9.0 (2015-09-14)
++++++++++++++++++

- Support for importing of historical data (`PR #44 <https://github.com/bradmontgomery/django-redis-metrics/pull/44>`_ thanks @smaccona)

0.8.3 (2015-03-11)
++++++++++++++++++

- bugfix: Include javascript static files in setup.py. (`PR #41 <https://github.com/bradmontgomery/django-redis-metrics/pull/41>`_)

0.8.2 (2015-01-19)
++++++++++++++++++

- support for weekly stats starting on mondays (`PR #16 <https://github.com/bradmontgomery/django-redis-metrics/pull/36>`_)
- optimized redis writes (`#37 <https://github.com/bradmontgomery/django-redis-metrics/issues/37>`_)
- Lower-cased JS files: changed ``Colors.js`` to ``colors.js`` and ``Chart.min.js`` to ``chart.min.js``

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
