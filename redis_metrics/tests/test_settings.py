from __future__ import unicode_literals
from django.test import TestCase
from django.test.utils import override_settings

from .. import settings as rs


@override_settings(REDIS_METRICS_HOST='localhost')
@override_settings(REDIS_METRICS_PORT=6379)
@override_settings(REDIS_METRICS_DB=0)
@override_settings(REDIS_METRICS_PASSWORD=None)
@override_settings(REDIS_METRICS_SOCKET_TIMEOUT=None)
@override_settings(REDIS_METRICS_SOCKET_CONNECTION_POOL=None)
@override_settings(REDIS_METRICS_MIN_GRANULARITY='seconds')
@override_settings(REDIS_METRICS_MAX_GRANULARITY='yearly')
@override_settings(REDIS_METRICS_MONDAY_FIRST_DAY_OF_WEEK=False)
class TestAppSettings(TestCase):

    def test_settings_getattr(self):
        self.assertEquals(rs.app_settings.REDIS_METRICS_HOST, 'localhost')
        self.assertEquals(rs.app_settings.REDIS_METRICS_PORT, 6379)
        self.assertEquals(rs.app_settings.REDIS_METRICS_DB, 0)
        self.assertEquals(rs.app_settings.REDIS_METRICS_PASSWORD, None)
        self.assertEquals(rs.app_settings.REDIS_METRICS_SOCKET_TIMEOUT, None)
        self.assertEquals(rs.app_settings.REDIS_METRICS_SOCKET_CONNECTION_POOL, None)
        self.assertEquals(rs.app_settings.REDIS_METRICS_MIN_GRANULARITY, 'seconds')
        self.assertEquals(rs.app_settings.REDIS_METRICS_MAX_GRANULARITY, 'yearly')
        self.assertEquals(rs.app_settings.REDIS_METRICS_MONDAY_FIRST_DAY_OF_WEEK, False)

    def test_settings_getitem(self):
        self.assertEquals(rs.app_settings['REDIS_METRICS_HOST'], 'localhost')
        self.assertEquals(rs.app_settings['REDIS_METRICS_PORT'], 6379)
        self.assertEquals(rs.app_settings['REDIS_METRICS_DB'], 0)
        self.assertEquals(rs.app_settings['REDIS_METRICS_PASSWORD'], None)
        self.assertEquals(rs.app_settings['REDIS_METRICS_SOCKET_TIMEOUT'], None)
        self.assertEquals(rs.app_settings['REDIS_METRICS_SOCKET_CONNECTION_POOL'], None)
        self.assertEquals(rs.app_settings['REDIS_METRICS_MIN_GRANULARITY'], 'seconds')
        self.assertEquals(rs.app_settings['REDIS_METRICS_MAX_GRANULARITY'], 'yearly')
        self.assertEquals(rs.app_settings['REDIS_METRICS_MONDAY_FIRST_DAY_OF_WEEK'], False)

    def test_settings_getattr_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            rs.app_settings.REDIS_METRICS_LOLWUT

    def test__test_granularities_constant(self):
        # Smoke test to catch myself when this changes.
        self.assertEqual(
            rs.GRANULARITIES,
            ['seconds', 'minutes', 'hourly', 'daily', 'weekly', 'monthly', 'yearly']
        )
