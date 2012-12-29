"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
import datetime
from mock import call, patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from .models import R


class TestR(TestCase):
    """Tests for the ``R`` class."""

    def setUp(self):
        self.old_host = getattr(settings, 'REDIS_METRICS_HOST', 'localhost')
        self.old_port = getattr(settings, 'REDIS_METRICS_PORT', 6379)
        self.old_db = getattr(settings, 'REDIS_METRICS_DB', 0)
        settings.REDIS_METRICS_HOST = 'localhost'
        settings.REDIS_METRICS_PORT = 6379
        settings.REDIS_METRICS_DB = 0

        # The redis client instance on R is a MagicMock object
        with patch('redis_metrics.models.redis'):
            self.r = R()
            self.redis = self.r.r  # keep a sanely named reference to Redis

    def tearDown(self):
        settings.REDIS_METRICS_HOST = self.old_host
        settings.REDIS_METRICS_PORT = self.old_port
        settings.REDIS_METRICS_DB = self.old_db
        super(TestR, self).tearDown()

    def test__date_range(self):
        """Tests ``R._date_range``."""

        # Verify that omitting the ``since`` parameter gives you dates for the
        # previous year.
        dates = [d for d in self.r._date_range()]
        self.assertEqual(len(dates), 365)

        # Provide a ``since`` parameter.
        t = datetime.date(2012, 12, 25)  # Merry Christmas!
        dates = [d for d in self.r._date_range(since=t)]

        self.assertIn(t, dates)  # Should include our specified date
        self.assertGreater(len(dates), 1)  # There should be some dates

    def test__build_keys(self):
        """Tests ``R._build_keys``. with default arguments."""
        d = datetime.date.today()
        slug = 'test-slug'
        expected_results = [
            "m:{0}:{1}".format(slug, d.strftime("%Y-%m-%d")),
            "m:{0}:w:{1}".format(slug, d.strftime("%U")),
            "m:{0}:m:{1}".format(slug, d.strftime("%Y-%m")),
            "m:{0}:y:{1}".format(slug, d.strftime("%Y")),
        ]
        keys = self.r._build_keys(slug)
        self.assertEqual(keys, expected_results)

    def test__build_keys_daily(self):
        """Tests ``R._build_keys``. with a *daily* granularity."""
        d = datetime.date(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='daily')
        self.assertEqual(keys, ['m:test-slug:2012-04-01'])

    def test__build_keys_weekly(self):
        """Tests ``R._build_keys``. with a *weekly* granularity."""
        d = datetime.date(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='weekly')
        self.assertEqual(keys, ['m:test-slug:w:14'])

    def test__build_keys_monthly(self):
        """Tests ``R._build_keys``. with a *monthly* granularity."""
        d = datetime.date(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='monthly')
        self.assertEqual(keys, ['m:test-slug:m:2012-04'])

    def test__build_keys_yearly(self):
        """Tests ``R._build_keys``. with a *yearly* granularity."""
        d = datetime.date(2012, 4, 1)  # April Fools!
        keys = self.r._build_keys('test-slug', date=d, granularity='yearly')
        self.assertEqual(keys, ['m:test-slug:y:2012'])

    def test_metric_slugs(self):
        """Test that ``R.metric_slugs`` makes a call to Redis SMEMBERS."""
        self.r.metric_slugs()
        self.redis.assert_has_calls([call.smembers(self.r._metric_slugs_key)])

    def test_metric(self):
        """Test setting metrics using ``R.metric``."""

        slug = 'test-metric'
        n = 1

        # get the keys used for the metric, so we can check for the appropriate
        # calls
        day, week, month, year = self.r._build_keys(slug)
        self.r.metric(slug, num=n)

        # Verify that setting a metric adds the appropriate slugs to the keys
        # set and then incrememts each key
        self.redis.assert_has_calls([
            call.sadd(self.r._metric_slugs_key, day, week, month, year),
            call.incr(day, n),
            call.incr(week, n),
            call.incr(month, n),
            call.incr(year, n),
        ])

    def test_get_metric(self):
        """Tests getting a single metric; ``R.get_metric``."""
        slug = 'test-metric'
        self.r.get_metric(slug)

        # Verify that we GET the keys from redis
        day, week, month, year = self.r._build_keys(slug)
        self.redis.assert_has_calls([
            call.get(day),
            call.get(week),
            call.get(month),
            call.get(year),
        ])

    def test_get_metrics(self):

        # Slugs for metrics we want
        slugs = ['metric-1', 'metric-2']

        # Build the various keys for each metric
        keys = []
        for s in slugs:
            day, week, month, year = self.r._build_keys(s)
            keys.extend([day, week, month, year])

        # construct the calls to redis
        calls = [call.get(k) for k in keys]

        # Test our method
        self.r.get_metrics(slugs)
        self.redis.assert_has_calls(calls)

    def _metric_history_keys(self, slug, since=None, granularity='daily'):
        """generates the same list of keys used in ``get_metric_history``.
        These can then be used to test for calls to redis. Note: This is
        duplicate code from ``get_metric_history`` :-/ """
        keys = set()
        for date in self.r._date_range(since):
            keys.update(set(self.r._build_keys(slug, date, granularity)))
        return keys

    def _test_get_metric_history(self, slug, granularity):
        """actual test code for ``R.get_metric_history``."""
        keys = self._metric_history_keys(slug, granularity=granularity)
        self.r.get_metric_history(slug, granularity=granularity)
        self.redis.assert_has_calls([call.mget(keys)])

    def test_get_metric_history_daily(self):
        """Tests ``R.get_metric_history`` with daily granularity."""
        self._test_get_metric_history('test-slug', 'daily')

    def test_get_metric_history_weekly(self):
        """Tests ``R.get_metric_history`` with weekly granularity."""
        self._test_get_metric_history('test-slug', 'weekly')

    def test_get_metric_history_monthly(self):
        """Tests ``R.get_metric_history`` with monthly granularity."""
        self._test_get_metric_history('test-slug', 'monthly')

    def test_get_metric_history_yearly(self):
        """Tests ``R.get_metric_history`` with yearly granularity."""
        self._test_get_metric_history('test-slug', 'yearly')

    def test_gauge_slugs(self):
        """Tests that ``R.gauge_slugs`` calls the SMEMBERS command."""
        self.r.gauge_slugs()
        self.redis.assert_has_calls([call.smembers(self.r._gauge_slugs_key)])

    def test__gauge_key(self):
        """Tests that ``R._gauge_key`` correctly generates gauge keys."""
        key = self.r._gauge_key('test-gauge')
        self.assertEqual(key, 'g:test-gauge')

    def test_gauge(self):
        """Tests setting a gauge with ``R.gauge``. Verifies that the gauge slug
        is added to the set of gauge slugs and that the value gets set."""
        self.r.gauge('test-gauge', 9000)
        self.redis.assert_has_calls([
            call.sadd(self.r._gauge_slugs_key, 'g:test-gauge'),
            call.set('g:test-gauge', 9000),
        ])

    def test_get_gauge(self):
        """Tests retrieving a gague with ``R.get_gauge``. Verifies that the
        Redis GET command is called with the correct key."""
        self.r.get_gauge('test-gauge')
        self.redis.assert_has_calls([call.get('g:test-gauge')])


class TestViews(TestCase):
    url = 'redis_metrics.urls'

    def setUp(self):
        self.user = User.objects.create_superuser(
            username="redis_metrics_test_user",
            email="redis_metrics_test_user@example.com",
            password="secret"
        )
        assert self.client.login(username="redis_metrics_test_user",
            password="secret")
        self.unauthed_client = Client()  # Keep an unauthenticated client

    def tearDown(self):
        self.user.delete()

    def assertUnauthedRequestRedirects(self, url):
        resp = self.unauthed_client.get(url)
        self.assertEqual(resp.status_code, 302)
        return resp

    def test_metrics_list(self):
        """Test the ``MetricsListView``."""
        url = reverse('redis_metrics_list')
        with patch('redis_metrics.views.R') as mock_r:
            # Set appropriate return values for methods that'll get called
            # in the MetricsListView.
            r = mock_r.return_value  # Get an instance of our Mocked R class
            r.metric_slugs.return_value = set(['test-metric'])
            r.gauge_slugs.return_value = set(['test-gauge'])

            # Do the Request and test for content
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('test-metric', resp.content)
            self.assertIn('test-gauge', resp.content)

            # Make sure our Mock R object called the right methods.
            mock_r.assert_has_calls([
                call().metric_slugs(),
                call().gauge_slugs(),
                call().get_gauge('test-gauge'),
            ])

    def test_metric_detail(self):
        slug = u'test-metric'
        url = reverse('redis_metric_detail', args=[slug])

        with patch('redis_metrics.views.R') as mock_r:
            # Set up a return value for ``R.get_metric(slug)``
            r = mock_r.return_value  # Get an instance of our Mocked R class
            m = {'day': '1', 'month': '1', 'week': '1', 'year': '1'}
            r.get_metric.return_value = m

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.context_data['slug'], slug)
            self.assertEqual(resp.context_data['metrics'], m)

            # Make sure our Mocked R instance had its ``get_metric`` method
            # called with the correct parameter
            r.assert_has_calls([call.get_metric(slug)])

    def test_metric_history(self):
        slug = u'test-metric'
        granularity = u'daily'
        url = reverse('redis_metric_history', args=[slug, granularity])

        with patch('redis_metrics.views.R') as mock_r:
            # Set up a return value for ``R
            r = mock_r.return_value  # Get an instance of our Mocked R class
            mocked_history = [
                ('m:{0}:2012-12-26'.format(slug), None),
                ('m:{0}:2012-12-27'.format(slug), None),
                ('m:{0}:2012-12-28'.format(slug), '1'),
            ]
            r.get_metric_history.return_value = mocked_history

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            context = resp.context_data
            self.assertEqual(context['slug'], slug)
            self.assertEqual(context['granularity'], granularity)
            self.assertEqual(context['metric_history'], mocked_history)

            # Make sure our Mocked R instance had its ``get_metric_history``
            # method called with the correct parameters
            r.assert_has_calls([
                call.get_metric_history(slug=slug, granularity=granularity)
            ])

    def test_metrics_list_requires_admin(self):
        """Verifies that ``MetricsListView`` requires authentication."""
        self.assertUnauthedRequestRedirects(reverse('redis_metrics_list'))

    def test_metric_detail_requires_admin(self):
        """Verifies that ``MetricDetailView`` requires authentication."""
        self.assertUnauthedRequestRedirects(
            reverse('redis_metric_detail', args=['whatever'])
        )

    def test_metric_history_requires_admin(self):
        """Verifies that ``MetricHistoryView`` requires authentication."""
        self.assertUnauthedRequestRedirects(
            reverse('redis_metric_history', args=['whatever', 'daily'])
        )
