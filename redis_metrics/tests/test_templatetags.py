#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import datetime, timedelta

from django.test import TestCase
from django.test.utils import override_settings
try:
    from unittest.mock import patch
except ImportError:
    from mock import call, patch  # NOQA
from redis_metrics.templatetags import redis_metric_tags as taglib
from redis_metrics.templatetags.redis_metrics_filters import (
    metric_slug, strip_metric_prefix, to_int, to_int_list
)


TEST_SETTINGS = {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0,
    'PASSWORD': None,
    'SOCKET_TIMEOUT': None,
    'SOCKET_CONNECTION_POOL': None,
    'MIN_GRANULARITY': 'seconds',
    'MAX_GRANULARITY': 'yearly',
    'MONDAY_FIRST_DAY_OF_WEEK': False,
}


@override_settings(REDIS_METRICS=TEST_SETTINGS)
class TestTemplateTags(TestCase):
    """Verify that template tags return the expected results."""
    maxDiff = None

    def setUp(self):
        """Patch the ``R`` class."""
        self.r_patcher = patch('redis_metrics.models.R')
        self.mock_r = self.r_patcher.start()

    def tearDown(self):
        self.r_patcher.stop()

    def test_metrics_since_history(self):
        """Tests the ``metrics_since`` template tag when displaying metric
        history."""

        slug = "test-slug"
        years = 5
        link_type = "history"
        now = datetime(2014, 7, 4)

        module = 'redis_metrics.templatetags.redis_metric_tags.datetime'
        with patch(module) as mock_datetime:
            mock_datetime.utcnow.return_value = now

            result = taglib.metrics_since(slug, years, link_type)
            self.assertIn('link_type', result.keys())
            self.assertIn('slug_values', result.keys())
            self.assertEqual(result['link_type'], link_type)

            # Verify contents of `slug_values`
            # There should be entries for each year + 5 additional periods.
            expected = [
                (slug, now - timedelta(days=1), "Today", 'daily'),
                (slug, now - timedelta(days=7), "1 Week", 'daily'),
                (slug, now - timedelta(days=30), "30 Days", 'daily'),
                (slug, now - timedelta(days=60), "60 Days", 'daily'),
                (slug, now - timedelta(days=90), "90 Days", 'daily'),
                (slug, now - timedelta(days=365), "1 Years", 'daily'),
                (slug, now - timedelta(days=365 * 2), "2 Years", 'daily'),
                (slug, now - timedelta(days=365 * 3), "3 Years", 'daily'),
                (slug, now - timedelta(days=365 * 4), "4 Years", 'daily'),
                (slug, now - timedelta(days=365 * 5), "5 Years", 'daily'),
            ]
            self.assertEqual(expected, result['slug_values'])

    def test_metrics_since_aggregate(self):
        """Tests the ``metrics_since`` template tag when displaying metric
        aggregate history."""

        slugs = ['test-a', 'test-b']
        years = 5
        link_type = "aggregate"
        granularity = "weekly"
        now = datetime(2014, 7, 4)

        module = 'redis_metrics.templatetags.redis_metric_tags.datetime'
        with patch(module) as mock_datetime:
            mock_datetime.utcnow.return_value = now

            result = taglib.metrics_since(slugs, years, link_type, granularity)
            self.assertIn('link_type', result.keys())
            self.assertIn('slug_values', result.keys())
            self.assertEqual(result['link_type'], link_type)

            # Verify contents of `slug_values`
            # There should be entries for each year + 5 additional periods.
            slugs = "+".join(slugs)
            expected = [
                (slugs, now - timedelta(days=1), "Today", granularity),
                (slugs, now - timedelta(days=7), "1 Week", granularity),
                (slugs, now - timedelta(days=30), "30 Days", granularity),
                (slugs, now - timedelta(days=60), "60 Days", granularity),
                (slugs, now - timedelta(days=90), "90 Days", granularity),
                (slugs, now - timedelta(days=365), "1 Years", granularity),
                (slugs, now - timedelta(days=365 * 2), "2 Years", granularity),
                (slugs, now - timedelta(days=365 * 3), "3 Years", granularity),
                (slugs, now - timedelta(days=365 * 4), "4 Years", granularity),
                (slugs, now - timedelta(days=365 * 5), "5 Years", granularity),
            ]
            self.assertEqual(expected, result['slug_values'])

    def test_gauge(self):
        """Tests the result of the gauge template tag."""
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            inst = mock_r.return_value
            inst.get_gauge.return_value = 100

            size = 50
            maximum = 200
            result = taglib.gauge("test-slug", maximum, size)
            expected_result = {
                'slug': "test-slug",
                'current_value': 100,
                'max_value': maximum,
                'size': size,
                'diff': maximum - 100
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_gauge.assert_called_once_with("test-slug")

    def test_gauge_when_overloaded(self):
        """Tests the result of a gauge whose current value > the maximum"""
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            inst = mock_r.return_value
            inst.get_gauge.return_value = 500

            size = 50
            maximum = 200
            result = taglib.gauge("test-slug", maximum, size)
            expected_result = {
                'slug': "test-slug",
                'current_value': 500,
                'max_value': maximum,
                'size': size,
                'diff': 0,  # deff should default to 0 when overloaded.
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_gauge.assert_called_once_with("test-slug")

    def test_metric_list(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            inst = mock_r.return_value
            inst.metric_slugs_by_category.return_value = "RESULT"

            result = taglib.metric_list()
            expected_result = {
                'metrics': "RESULT",
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.metric_slugs_by_category.assert_called_once_with()

    def test_metric_detail(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            inst = mock_r.return_value
            inst._granularities.return_value = ['daily', 'weekly']
            inst.get_metric.return_value = {
                'daily': 1,
                'weekly': 2,
            }

            result = taglib.metric_detail('test')
            expected_result = {
                'granularities': ['Daily', 'Weekly'],
                'metrics': [('daily', 1), ('weekly', 2)],
                'slug': 'test',
                'with_data_table': False,
            }

            self.assertDictEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_metric.assert_called_once_with('test')

    def test_metric_history(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            history = [("m:test:2000-01-01", 42)]
            inst = mock_r.return_value
            inst.get_metric_history.return_value = history

            result = taglib.metric_history('test')
            expected_result = {
                'slug': 'test',
                'granularity': "daily",
                'metric_history': history,
                'since': None,
                'to': None,
                'with_data_table': False,
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_metric_history.assert_called_once_with(
                slugs='test',
                granularity='daily',
                since=None,
                to=None
            )

    def test_metric_history_with_date(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            history = [("m:test:2000-01-01", 42)]
            inst = mock_r.return_value
            inst.get_metric_history.return_value = history
            expected_result = {
                'slug': 'test',
                'granularity': "daily",
                'metric_history': history,
                'since': None,
                'to': None,
                'with_data_table': False,
            }

            # With a date string
            since = datetime(2000, 1, 2)
            expected_result['since'] = since
            result = taglib.metric_history('test', since="2000-01-02")
            self.assertEqual(result, expected_result)
            inst.get_metric_history.assert_called_once_with(
                slugs='test',
                granularity='daily',
                since=since,
                to=None,
            )
            inst.reset_mock()

            # With a datetime string
            since = datetime(2000, 1, 2, 11, 30, 45)
            expected_result['since'] = since
            result = taglib.metric_history('test', since="2000-01-02 11:30:45")
            self.assertEqual(result, expected_result)
            inst.get_metric_history.assert_called_once_with(
                slugs='test',
                granularity='daily',
                since=since,
                to=None
            )
            inst.reset_mock()

            # With a datetime object
            since = datetime(2000, 1, 2, 11, 30, 45)
            expected_result['since'] = since
            result = taglib.metric_history('test', since=since)
            self.assertEqual(result, expected_result)
            inst.get_metric_history.assert_called_once_with(
                slugs='test',
                granularity='daily',
                since=since,
                to=None
            )
            inst.reset_mock()

            # With both a since and to parameter
            since = datetime(2000, 1, 2, 11, 30, 45)
            to = datetime(2001, 1, 2, 11, 30, 45)
            expected_result['since'] = since
            expected_result['to'] = to
            result = taglib.metric_history('test', since=since, to=to)
            self.assertEqual(result, expected_result)
            inst.get_metric_history.assert_called_once_with(
                slugs='test',
                granularity='daily',
                since=since,
                to=to
            )

    def test_aggregate_detail(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            slugs = ['a1', 'a2']
            inst = mock_r.return_value
            inst._granularities.return_value = ['daily', 'weekly', 'monthly', 'yearly']
            inst.get_metrics.return_value = [
                ('a1', {'day': 1, 'week': 2, 'month': 3, 'year': 4}),
                ('a2', {'day': 3, 'week': 6, 'month': 9, 'year': 12}),
            ]

            result = taglib.aggregate_detail(slugs)
            expected_result = {
                'chart_id': 'metric-aggregate-a1-a2',
                'granularities': ['Day', 'Week', 'Month', 'Year'],
                'slugs': slugs,
                'metrics': [
                    ('a1', [1, 2, 3, 4]),
                    ('a2', [3, 6, 9, 12]),
                ],
                'with_data_table': False,
            }

            self.assertDictEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_metrics.assert_called_once_with(slugs)

    def test_aggregate_history(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            history = {
                'periods': ['2000-01-01', '2000-01-02', '2000-01-03'],
                'data': [
                    {
                        'slug': 'bar',
                        'values': [1, 2, 3]
                    },
                    {
                        'slug': 'foo',
                        'values': [4, 5, 6]
                    },
                ]
            }
            inst = mock_r.return_value
            inst.get_metric_history_chart_data.return_value = history

            result = taglib.aggregate_history(['foo', 'bar'])
            expected_result = {
                'chart_id': 'metric-aggregate-history-foo-bar',
                'slugs': ['foo', 'bar'],
                'since': None,
                'granularity': "daily",
                'metric_history': history,
                'with_data_table': False,
            }

            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()  # Create the R object
            inst.get_metric_history_chart_data.assert_called_once_with(
                slugs=['foo', 'bar'],
                since=None,
                granularity='daily'
            )

    def test_aggregate_history_with_date(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.get_r") as mock_r:
            history = {
                'periods': ['2000-01-01', '2000-01-02', '2000-01-03'],
                'data': [
                    {
                        'slug': 'bar',
                        'values': [1, 2, 3]
                    },
                    {
                        'slug': 'foo',
                        'values': [4, 5, 6]
                    },
                ]
            }
            inst = mock_r.return_value
            inst.get_metric_history_chart_data.return_value = history
            slugs = ['foo', 'bar']
            expected_result = {
                'chart_id': 'metric-aggregate-history-foo-bar',
                'slugs': slugs,
                'since': None,
                'granularity': "daily",
                'metric_history': history,
                'with_data_table': False,
            }

            # When given a date string
            result = taglib.aggregate_history(slugs, since="2000-01-02")
            expected_result['since'] = datetime(2000, 1, 2)
            self.assertEqual(result, expected_result)

            # When given a datetime
            result = taglib.aggregate_history(slugs, since="2000-01-02 11:30:45")
            expected_result['since'] = datetime(2000, 1, 2, 11, 30, 45)
            self.assertEqual(result, expected_result)

            # When given a datetime object
            d = datetime(2000, 1, 2, 11, 30, 45)
            result = taglib.aggregate_history(slugs, since=d)
            expected_result['since'] = d
            self.assertEqual(result, expected_result)


class TestTemplateFilters(TestCase):
    """Verify that the custom filters return expected results."""

    def test_to_int_list(self):
        """Verify that the ``int_list`` filter converts strings to numbers and that
        it returns 0 when given unexpected values."""
        self.assertEqual(to_int_list([u"3", None, "asdf", u"42"]), [3, 0, 0, 42])

    def test_to_int(self):
        """Verify that the ``int`` filter converts strings to numbers and that
        it returns 0 when given unexpected values."""
        self.assertEqual(to_int(u"3"), 3)
        self.assertEqual(to_int(u"asdf"), 0)
        self.assertEqual(to_int(None), 0)

    def test_strip_metric_prefix(self):
        # Seconds -- from: ``m:<slug>:s:<yyyy-mm-dd-hh-MM-SS>`` to ``<yyyy-mm-dd-hh-MM-SS>``
        self.assertEqual(
            strip_metric_prefix("m:test:s:2000-01-30-14-45-37"), "s:2000-01-30-14-45-37"
        )

        # Minutes -- from: ``m:<slug>:i:<yyyy-mm-dd-hh-MM>`` to ``<yyyy-mm-dd-hh-MM>``
        self.assertEqual(
            strip_metric_prefix("m:test:i:2000-01-30-14-45"), "i:2000-01-30-14-45"
        )

        # Hourly -- from: ``m:<slug>:h:<yyyy-mm-dd-hh>`` to ``<yyyy-mm-dd-hh>``
        self.assertEqual(
            strip_metric_prefix("m:test:h:2000-01-30-00"), "h:2000-01-30-00"
        )

        # Daily -- from: ``m:<slug>:<yyyy-mm-dd>`` to ``<yyyy-mm-dd>``
        self.assertEqual(
            strip_metric_prefix("m:test:2000-01-30"), "2000-01-30"
        )

        # Weekly -- from ``m:<slug>:w:<yyyy-num>`` to ``w:<yyyy-num>``
        self.assertEqual(
            strip_metric_prefix("m:test:w:2000-52"), "w:2000-52"
        )

        # Monthly -- from ``m:<slug>:m:<yyyy-mm>`` to ``m:<yyyy-mm>``
        self.assertEqual(
            strip_metric_prefix("m:test:m:2000-01"), "m:2000-01"
        )

        # Yearly -- from ``m:<slug>:y:<yyyy>`` to ``y:<yyyy>``
        self.assertEqual(
            strip_metric_prefix("m:test:y:2000"), "y:2000"
        )

    def test_metric_slug(self):
        # Converts ``m:foo:s:<yyyy-mm-dd-hh-mm-ss>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:s:2000-01-31-14-45-37"), "foo")

        # Converts ``m:foo:i:<yyyy-mm-dd-hh-mm>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:i:2000-01-31-14-45"), "foo")

        # Converts ``m:foo:h:<yyyy-mm-dd-hh>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:h:2000-01-31-14"), "foo")

        # Converts ``m:foo:<yyyy-mm-dd>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:2000-01-31"), "foo")

        # Converts ``m:foo:w:<yyyy-num>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:w:2000-52"), "foo")

        # Converts ``m:foo:m:<yyyy-mm>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:m:2000-01"), "foo")

        # Converts ``m:foo:y:<yyyy>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:y:2000"), "foo")
