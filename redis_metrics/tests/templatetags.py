#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from mock import patch
from redis_metrics.templatetags.gauges import gauge


class TestTemplateTags(TestCase):
    """Verify that template tags return the expected results."""

    def setUp(self):
        """Patch the ``R`` class."""
        self.r_patcher = patch('redis_metrics.models.R')
        self.mock_r = self.r_patcher.start()

    def tearDown(self):
        self.r_patcher.stop()

    def test_gauge(self):
        with patch("redis_metrics.templatetags.gauges.R") as mock_r:
            inst = mock_r.return_value
            inst.get_gauge.return_value = 100

            result = gauge("test-slug", 1000, 50)
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
