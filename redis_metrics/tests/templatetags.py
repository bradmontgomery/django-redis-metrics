#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from mock import patch
from redis_metrics.templatetags import redis_metric_tags as taglib
from redis_metrics.templatetags.redis_metrics_filters import (
    strip_metric_prefix, metric_slug
)


class TestTemplateTags(TestCase):
    """Verify that template tags return the expected results."""

    def setUp(self):
        """Patch the ``R`` class."""
        self.r_patcher = patch('redis_metrics.models.R')
        self.mock_r = self.r_patcher.start()

    def tearDown(self):
        self.r_patcher.stop()

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


class TestTemplateFilters(TestCase):
    """Verify that the custom filters return expected results."""

    def test_strip_metric_prefix(self):
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
        # Converts ``m:foo:<yyyy-mm-dd>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:2000-01-31"), "foo")

        # Converts ``m:foo:w:<yyyy-num>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:w:2000-52"), "foo")

        # Converts ``m:foo:m:<yyyy-mm>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:m:2000-01"), "foo")

        # Converts ``m:foo:y:<yyyy>`` to ``foo``
        self.assertEqual(metric_slug("m:foo:y:2000"), "foo")
