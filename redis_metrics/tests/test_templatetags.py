#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta

from django.test import TestCase
from mock import patch
from redis_metrics.templatetags import redis_metric_tags as taglib
from redis_metrics.templatetags.redis_metrics_filters import (
    metric_slug, strip_metric_prefix, to_int
)


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
        with patch("redis_metrics.templatetags.redis_metric_tags.R") as mock_r:
            inst = mock_r.return_value
            inst.get_gauge.return_value = 100

            result = taglib.gauge("test-slug", 1000, 50)
            expected_result = {
                'slug': "test-slug",
                'current_value': 100,
                'max_value': 1000,
                'size': 50,
                'yellow': 1000 - (1000 / 2),
                'red': 1000 - (1000 / 4),
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_gauge.assert_called_once_with("test-slug")

    def test_metric_list(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.R") as mock_r:
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
        with patch("redis_metrics.templatetags.redis_metric_tags.R") as mock_r:
            inst = mock_r.return_value
            inst.get_metric.return_value = "RESULT"

            result = taglib.metric_detail('test')
            expected_result = {
                'slug': 'test',
                'metrics': "RESULT",
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_metric.assert_called_once_with('test')

    def test_metric_history(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.R") as mock_r:
            history = [("m:test:2000-01-01", 42)]
            inst = mock_r.return_value
            inst.get_metric_history.return_value = history

            result = taglib.metric_history('test')
            expected_result = {
                'slug': 'test',
                'granularity': "daily",
                'metric_history': history,
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_metric_history.assert_called_once_with(
                slugs='test',
                granularity='daily',
                since=None
            )

    def test_aggregate_detail(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.R") as mock_r:
            slugs = ['a1', 'a2']
            inst = mock_r.return_value
            inst.get_metrics.return_value = 'RESULTS'

            result = taglib.aggregate_detail(slugs)
            expected_result = {
                'slugs': slugs,
                'metrics': 'RESULTS',
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_metrics.assert_called_once_with(slugs)

    def test_aggregate_history(self):
        with patch("redis_metrics.templatetags.redis_metric_tags.R") as mock_r:
            history = [
                ('Period', 'foo', 'bar'),
                (u'2000-01-01', '100', '200'),
                (u'2000-01-02', '200', '300'),
                (u'2000-01-02', '300', '400'),
            ]
            inst = mock_r.return_value
            inst.get_metric_history_as_columns.return_value = history

            result = taglib.aggregate_history(set(['foo', 'bar']))
            expected_result = {
                'slugs': ['foo', 'bar'],
                'granularity': "daily",
                'metric_history': history,
            }
            self.assertEqual(result, expected_result)
            mock_r.assert_called_once_with()
            inst.get_metric_history_as_columns.assert_called_once_with(
                slugs=['foo', 'bar'],
                since=None,
                granularity='daily'
            )


class TestTemplateFilters(TestCase):
    """Verify that the custom filters return expected results."""

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
