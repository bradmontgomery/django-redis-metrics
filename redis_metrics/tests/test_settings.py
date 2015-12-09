from __future__ import unicode_literals
from django.test import TestCase
from django.test.utils import override_settings

from .. import settings as rs


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
class TestAppSettings(TestCase):

    def test_settings_getattr(self):
        self.assertEquals(rs.app_settings.HOST, 'localhost')
        self.assertEquals(rs.app_settings.PORT, 6379)
        self.assertEquals(rs.app_settings.DB, 0)
        self.assertEquals(rs.app_settings.PASSWORD, None)
        self.assertEquals(rs.app_settings.SOCKET_TIMEOUT, None)
        self.assertEquals(rs.app_settings.SOCKET_CONNECTION_POOL, None)
        self.assertEquals(rs.app_settings.MIN_GRANULARITY, 'seconds')
        self.assertEquals(rs.app_settings.MAX_GRANULARITY, 'yearly')
        self.assertEquals(rs.app_settings.MONDAY_FIRST_DAY_OF_WEEK, False)

    def test_settings_getitem(self):
        self.assertEquals(rs.app_settings['HOST'], 'localhost')
        self.assertEquals(rs.app_settings['PORT'], 6379)
        self.assertEquals(rs.app_settings['DB'], 0)
        self.assertEquals(rs.app_settings['PASSWORD'], None)
        self.assertEquals(rs.app_settings['SOCKET_TIMEOUT'], None)
        self.assertEquals(rs.app_settings['SOCKET_CONNECTION_POOL'], None)
        self.assertEquals(rs.app_settings['MIN_GRANULARITY'], 'seconds')
        self.assertEquals(rs.app_settings['MAX_GRANULARITY'], 'yearly')
        self.assertEquals(rs.app_settings['MONDAY_FIRST_DAY_OF_WEEK'], False)

    def test_settings_getattr_raises_attribute_error(self):
        with self.assertRaises(AttributeError):
            rs.app_settings.LOLWUT

    def test__test_granularities_constant(self):
        # Smoke test to catch myself when this changes.
        self.assertEqual(
            rs.GRANULARITIES,
            ['seconds', 'minutes', 'hourly', 'daily', 'weekly', 'monthly', 'yearly']
        )
