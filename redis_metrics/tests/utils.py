from datetime import date, timedelta
from mock import call, patch, Mock

from django.conf import settings
from django.test import TestCase

from ..models import R
from .. import utils


class TestUtils(TestCase):
    """Tests for functions in ``redis_metrics.utils``."""

    def setUp(self):
        self.old_host = getattr(settings, 'REDIS_METRICS_HOST', 'localhost')
        self.old_port = getattr(settings, 'REDIS_METRICS_PORT', 6379)
        self.old_db = getattr(settings, 'REDIS_METRICS_DB', 0)
        settings.REDIS_METRICS_HOST = 'localhost'
        settings.REDIS_METRICS_PORT = 6379
        settings.REDIS_METRICS_DB = 0

        # The redis client instance on R is a MagicMock object
        # TODO: create a patcher for StrictRedis

    def tearDown(self):
        settings.REDIS_METRICS_HOST = self.old_host
        settings.REDIS_METRICS_PORT = self.old_port
        settings.REDIS_METRICS_DB = self.old_db
        super(TestUtils, self).tearDown()

        # TODO: unpatch StrictRedis

    def test_get_r(self):
        # Global `_redis_model` is None by default
        self.assertEqual(utils._redis_model, None)
        with patch("redis_metrics.models.redis.StrictRedis") as mock_redis:
            r = utils.get_r()
            self.assertIsInstance(r, R)
            self.assertEqual(r, utils._redis_model)
            mock_redis.assert_called_once_with(
                host="localhost", port=6379, db=0, password=None,
                     connection_pool=None, socket_timeout=None)

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

    def test__dates(self):
        # The following line is the expected result of _dates for 5 days
        expected = (date.today() - timedelta(days=d) for d in range(5))
        result = utils._dates(5)
        self.assertEqual(type(expected), type(result))
        self.assertEqual(list(utils._dates(5)), list(expected))

    def test_generate_test_metrics(self):
        config = {
            '_build_keys.return_value': ['key'],
            '_metric_slugs_key': 'MSK',
        }
        mock_r = Mock(**config)
        config = {'return_value': mock_r}
        with patch("redis_metrics.utils.get_r", **config) as mock_get_r:
            # When called with random = True
            with patch("redis_metrics.utils.random") as mock_random:
                mock_random.randint.return_value = 9999
                utils.generate_test_metrics(
                    slug="test_slug", num=1, randomize=True)
                mock_get_r.assert_called_once_with()
                mock_r.r.sadd.assert_called_once_with('MSK', 'key')
                mock_random.seed.assert_called_once_with()
                mock_random.randint.assert_called_once_with(0, 100 + 100)
                mock_r.r.incr.assert_called_once_with('key', 9999)

            mock_get_r.reset_mock()
            mock_r.reset_mock()

            # When called with random = False
            utils.generate_test_metrics(
                slug="test_slug", num=1, randomize=False)
            mock_get_r.assert_called_once_with()
            mock_r.r.sadd.assert_called_once_with('MSK', 'key')
            mock_r.r.incr.assert_called_once_with('key', 100)

    def test_delete_test_metrics(self):
        d = list(utils._dates(1))[0]  # Date used inside function
        with patch('redis_metrics.utils.get_r') as mock_get_r:
            mock_r = mock_get_r.return_value
            mock_r._metric_slugs_key = 'MSK'
            mock_r._build_keys.return_value = ['keys']

            utils.delete_test_metrics(slug="test-metric", num=1)
            mock_r._build_keys.assert_called_once_with("test-metric", date=d)
            mock_r.r.srem.assert_called_once_with('MSK', 'keys')
            mock_r.r.delete.assert_called_once_with('keys')
