from datetime import datetime
from mock import call, patch, Mock

from django.conf import settings
from django.test import TestCase

from ..models import R
from ..settings import app_settings
from .. import utils


class TestUtils(TestCase):
    """Tests for functions in ``redis_metrics.utils``."""

    def setUp(self):
        self.old_host = app_settings['REDIS_METRICS_HOST']
        self.old_port = app_settings['REDIS_METRICS_PORT']
        self.old_db = app_settings['REDIS_METRICS_DB']
        self.old_password = app_settings['REDIS_METRICS_PASSWORD']
        self.old_socket_timeout = app_settings['REDIS_METRICS_SOCKET_TIMEOUT']
        self.old_connection_pool = app_settings['REDIS_METRICS_SOCKET_CONNECTION_POOL']

        settings.REDIS_METRICS_HOST = 'localhost'
        settings.REDIS_METRICS_PORT = 6379
        settings.REDIS_METRICS_DB = 0
        settings.REDIS_METRICS_PASSWORD = None
        settings.REDIS_METRICS_SOCKET_TIMEOUT = None
        settings.REDIS_METRICS_SOCKET_CONNECTION_POOL = None

        # The redis client instance on R is a MagicMock object
        # TODO: create a patcher for StrictRedis

    def tearDown(self):
        settings.REDIS_METRICS_HOST = self.old_host
        settings.REDIS_METRICS_PORT = self.old_port
        settings.REDIS_METRICS_DB = self.old_db
        settings.REDIS_METRICS_PASSWORD = self.old_password
        settings.REDIS_METRICS_SOCKET_TIMEOUT = self.old_socket_timeout
        settings.REDIS_METRICS_SOCKET_CONNECTION_POOL = self.old_connection_pool
        super(TestUtils, self).tearDown()

        # TODO: unpatch StrictRedis

    def test_get_r(self):
        # Global `_redis_model` is None by default
        r_kwargs = {
            'decode_responses': True,
            'host': 'localhost',
            'db': 0,
            'port': 6379,
            'password': None,
            'connection_pool': None,
            'socket_timeout': None
        }
        with patch('redis_metrics.models.redis.StrictRedis') as mock_redis:
            inst = R()
            self.assertEqual(inst.host, 'localhost')
            self.assertEqual(inst.port, 6379)
            self.assertEqual(inst.db, 0)
            self.assertEqual(inst.password, None)
        self.assertEqual(utils._redis_model, None)
        with patch("redis_metrics.models.redis.StrictRedis") as mock_redis:
            r = utils.get_r()
            self.assertIsInstance(r, R)
            self.assertEqual(r, utils._redis_model)
            mock_redis.assert_called_once_with(**r_kwargs)

    def test_set_metric(self):
        with patch("redis_metrics.utils.get_r") as mock_get_r:
            utils.set_metric("test-slug", 42)
            mock_get_r.assert_has_calls([
                call(),
                call().set_metric("test-slug", 42, category=None, expire=None),
            ])

    def test_set_metric_with_category(self):
        with patch("redis_metrics.utils.get_r") as mock_get_r:
            utils.set_metric("test-slug", 42, category="Woo")
            mock_get_r.assert_has_calls([
                call(),
                call().set_metric("test-slug", 42, category="Woo", expire=None),
            ])

    def test_set_metric_with_expiration(self):
        with patch("redis_metrics.utils.get_r") as mock_get_r:
            utils.set_metric("test-slug", 42, expire=300)
            mock_get_r.assert_has_calls([
                call(),
                call().set_metric("test-slug", 42, category=None, expire=300),
            ])

    def test_metric(self):
        with patch("redis_metrics.utils.get_r") as mock_get_r:
            utils.metric("test-slug")
            mock_get_r.assert_has_calls([
                call(),
                call().metric("test-slug", num=1, category=None, expire=None),
            ])

    def test_metric_with_category(self):
        with patch("redis_metrics.utils.get_r") as mock_get_r:
            utils.metric("test-slug", category="Woo")
            mock_get_r.assert_has_calls([
                call(),
                call().metric("test-slug", num=1, category="Woo", expire=None),
            ])

    def test_metric_with_expiration(self):
        with patch("redis_metrics.utils.get_r") as mock_get_r:
            utils.metric("test-slug", expire=300)
            mock_get_r.assert_has_calls([
                call(),
                call().metric("test-slug", num=1, category=None, expire=300),
            ])

    def test_gauge(self):
        with patch("redis_metrics.utils.get_r") as mock_get_r:
            utils.gauge("test-slug", 9000)
            mock_get_r.assert_has_calls([
                call(),
                call().gauge("test-slug", 9000),
            ])

    def test_generate_test_metrics(self):
        keys = [
            'm:test-slug:s:2000-01-02-03-04-05',
            'm:test-slug:i:2000-01-02-03-04',
            'm:test-slug:h:2000-01-02-03',
            'm:test-slug:2000-01-02',
            'm:test-slug:w:2000-01',
            'm:test-slug:m:2000-01',
            'm:test-slug:y:2000',
        ]
        config = {
            '_build_keys.return_value': keys,
            '_metric_slugs_key': 'MSK',
            '_date_range.return_value': [datetime.utcnow()],
        }
        mock_r = Mock(**config)
        config = {'return_value': mock_r}
        with patch("redis_metrics.utils.get_r", **config) as mock_get_r:
            # When called with random = True
            with patch("redis_metrics.utils.random") as mock_random:
                mock_random.randint.return_value = 9999
                utils.generate_test_metrics(
                    slug="test-slug", num=1, randomize=True, increment_value=1
                )
                mock_get_r.assert_called_once_with()
                mock_r.r.sadd.assert_called_once_with('MSK', 'test-slug')
                mock_random.seed.assert_called_once_with()
                mock_random.randint.assert_has_calls([
                    call(0, 1), call(0, 1), call(0, 1), call(0, 1),
                ])
                mock_r.r.incr.assert_has_calls([
                    call('m:test-slug:2000-01-02', 9999),
                    call('m:test-slug:w:2000-01', 9999),
                    call('m:test-slug:m:2000-01', 9999),
                    call('m:test-slug:y:2000', 9999),
                ])

            mock_get_r.reset_mock()
            mock_r.reset_mock()

            # When called with random = False
            utils.generate_test_metrics(
                slug="test-slug", num=1, randomize=False, increment_value=1
            )
            mock_get_r.assert_called_once_with()
            mock_r.r.sadd.assert_called_once_with('MSK', 'test-slug')
            mock_r.r.incr.assert_has_calls([
                call('m:test-slug:2000-01-02', 0),
                call('m:test-slug:w:2000-01', 0),
                call('m:test-slug:m:2000-01', 0),
                call('m:test-slug:y:2000', 0),
            ])

    def test_generate_test_metrics_with_cap(self):
        keys = [
            'm:test-slug:s:2000-01-02-03-04-05',
            'm:test-slug:i:2000-01-02-03-04',
            'm:test-slug:h:2000-01-02-03',
            'm:test-slug:2000-01-02',
            'm:test-slug:w:2000-01',
            'm:test-slug:m:2000-01',
            'm:test-slug:y:2000',
        ]
        config = {
            '_build_keys.return_value': keys,
            '_metric_slugs_key': 'MSK',
            'r.get.return_value': 100,
            '_date_range.return_value': [datetime.utcnow()],
        }
        mock_r = Mock(**config)
        config = {'return_value': mock_r}
        with patch("redis_metrics.utils.get_r", **config) as mock_get_r:
            # When called with random = True
            with patch("redis_metrics.utils.random") as mock_random:
                mock_random.randint.return_value = 9999
                utils.generate_test_metrics(
                    slug="test-slug", num=1, randomize=True, cap=5, increment_value=1
                )
                mock_get_r.assert_called_once_with()
                mock_r.r.sadd.assert_called_once_with('MSK', 'test-slug')
                mock_random.seed.assert_called_once_with()
                mock_random.randint.assert_has_calls([
                    call(0, 1), call(0, 1), call(0, 1), call(0, 1),
                ])
                # Should be no increment due to cap
                mock_r.r.incr.assert_has_calls([
                    call('m:test-slug:2000-01-02', 0),
                    call('m:test-slug:w:2000-01', 0),
                    call('m:test-slug:m:2000-01', 0),
                    call('m:test-slug:y:2000', 0),
                ])

            mock_get_r.reset_mock()
            mock_r.reset_mock()

    def test_delete_test_metrics(self):
        d = datetime.utcnow()
        with patch('redis_metrics.utils.get_r') as mock_get_r:
            mock_r = mock_get_r.return_value
            mock_r._metric_slugs_key = 'MSK'
            mock_r._build_keys.return_value = ['keys']
            mock_r._date_range.return_value = [d]

            utils.delete_test_metrics(slug="test-metric", num=1)
            mock_r._build_keys.assert_called_once_with("test-metric", date=d)
            mock_r.r.srem.assert_called_once_with('MSK', 'test-metric')
            mock_r.r.delete.assert_called_once_with('keys')
