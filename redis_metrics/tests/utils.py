from mock import patch
from django.conf import settings
from django.test import TestCase

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
        assert False

    def test_metric(self):
        assert False

    def test_gauge(self):
        assert False

    def test__dates(self):
        assert False

    def test_generate_test_metrics(self):
        assert False

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
