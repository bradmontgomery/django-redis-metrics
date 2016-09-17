"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from __future__ import unicode_literals
from datetime import datetime
try:
    from unittest.mock import call, patch
except ImportError:
    from mock import call, patch

from django.core.urlresolvers import reverse
from django.test import TestCase, Client
from django.test.utils import override_settings


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
class TestViews(TestCase):
    url = 'redis_metrics.urls'

    def _get_user_model(self):
        try:  # pragma: no cover
            # Django >= 1.5
            from django.contrib.auth import get_user_model  # pragma: no cover
            User = get_user_model()  # pragma: no cover
        except ImportError:  # pragma: no cover
            # Fallback for Django 1.4 (or lower)
            from django.contrib.auth.models import User  # pragma: no cover
        return User

    def setUp(self):
        # Patch the connection to redis, but keep a reference to the
        # created StrictRedis instance, so we can make assertions about how
        # it's called.
        self.redis_patcher = patch('redis_metrics.models.redis.StrictRedis')
        mock_StrictRedis = self.redis_patcher.start()
        self.redis = mock_StrictRedis.return_value

        User = self._get_user_model()
        self.user = User.objects.create_superuser(
            username="redis_metrics_test_user",
            email="redis_metrics_test_user@example.com",
            password="secret"
        )
        assert self.client.login(
            username="redis_metrics_test_user",
            password="secret")
        self.unauthed_client = Client()  # Keep an unauthenticated client

    def tearDown(self):
        self.redis_patcher.stop()
        self.user.delete()

    def assertUnauthedRequestRedirects(self, url):
        resp = self.unauthed_client.get(url)
        self.assertEqual(resp.status_code, 302)
        return resp

    def test_default_view(self):
        url = reverse('redis_metrics_default')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "redis_metrics/default.html")

    def test_gauges_view(self):
        """Test the ``GaugesView``."""
        url = reverse('redis_metrics_gauges')
        with patch('redis_metrics.views.get_r') as mock_r:
            # Set appropriate return values for methods that'll get called
            # in the MetricsListView.
            r = mock_r.return_value  # Get an instance of our Mocked R class
            r.gauge_slugs.return_value = set(['gauge-a', 'gauge-b'])

            # Do the Request and test for content
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Gauges', str(resp.content))
            self.assertEqual(
                resp.context['gauges'],
                set(['gauge-a', 'gauge-b'])
            )

            # Make sure our Mock R object called the right methods.
            mock_r.assert_has_calls([call().gauge_slugs()])

    def test_metrics_list(self):
        """Test the ``MetricsListView``."""
        url = reverse('redis_metrics_list')
        with patch('redis_metrics.views.get_r') as mock_r:
            # Set appropriate return values for methods that'll get called
            # in the MetricsListView.
            r = mock_r.return_value  # Get an instance of our Mocked R class
            r.metric_slugs_by_category.return_value = {
                "Sample Category": ['test-metric-a', 'test-metric-b'],
            }
            r.gauge_slugs.return_value = set(['test-gauge'])

            # Do the Request and test for content
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('Sample Category', resp.context['metrics'].keys())

            metrics_values = list(resp.context['metrics'].values())
            self.assertIn('test-metric-a', metrics_values[0])
            self.assertIn('test-metric-b', metrics_values[0])

            # Make sure our Mock R object called the right methods.
            mock_r.assert_has_calls([
                call().metric_slugs_by_category(),
            ])

    def test_metric_detail(self):
        with patch('redis_metrics.views.get_r') as mock_get_r:
            inst = mock_get_r.return_value
            inst._granularities.return_value = ['daily', 'weekly']

            slug = 'test-metric'
            url = reverse('redis_metric_detail', args=[slug])

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.context_data['slug'], slug)
            self.assertEqual(resp.context_data['granularities'], ['daily', 'weekly'])

    def test_metric_history(self):
        with patch('redis_metrics.views.get_r') as mock_get_r:
            inst = mock_get_r.return_value
            inst._granularities.return_value = ['daily', 'weekly']

            slug = 'test-metric'
            granularity = 'daily'
            url = reverse('redis_metric_history', args=[slug, granularity])

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            context = resp.context_data
            self.assertEqual(context['slug'], slug)
            self.assertEqual(context['since'], None)
            self.assertEqual(context['granularity'], granularity)
            self.assertEqual(context['granularities'], ['daily', 'weekly'])

    def test_metric_history_since(self):
        """Tests the ``MetricHistoryView`` when there's a ``since`` variable"""
        slug = 'test-metric'
        granularity = 'daily'
        url = reverse('redis_metric_history', args=[slug, granularity])

        # Do the Request & test results for a Date
        resp = self.client.get(url, {'since': '2012-12-25'})
        self.assertEqual(resp.status_code, 200)
        context = resp.context_data
        self.assertEqual(context['since'], datetime(2012, 12, 25))
        self.assertEqual(context['slug'], slug)
        self.assertEqual(context['granularity'], granularity)

        # Do the Request & test results for a Date & Time
        resp = self.client.get(url, {'since': '2012-12-25 11:30:45'})
        self.assertEqual(resp.status_code, 200)
        context = resp.context_data
        self.assertEqual(context['since'], datetime(2012, 12, 25, 11, 30, 45))
        self.assertEqual(context['slug'], slug)
        self.assertEqual(context['granularity'], granularity)

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

    def test_aggregate_form_view(self):
        """Verifies that GET requests to the ``AggregateFormView`` have the
        correct context info (i.e. a form)."""
        url = reverse('redis_metric_aggregate')
        self.assertUnauthedRequestRedirects(url)
        with patch('redis_metrics.views.get_r'):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('form', resp.context_data)

    def test_aggregate_form_view_post(self):
        """Verifies that POST requests to the ``AggregateFormView`` work as
        expected."""
        url = reverse('redis_metric_aggregate')
        with patch('redis_metrics.views.get_r'):
            with patch('redis_metrics.forms.R') as mock_r:
                # Set up a return value for ``R.metric_slugs``, which is used
                # in the ``AggregateMetricForm``
                r = mock_r.return_value  # An instance of our Mocked R class
                r.metric_slugs.return_value = set(['test', 'foo', 'bar'])

                # Test with ONE metric selected
                data = {'metrics': ['foo']}
                resp = self.client.post(url, data)
                self.assertEqual(resp.status_code, 302)
                # make sure the metric slug shows up in the redirect URL
                self.assertIn('foo', resp.get("Location", ''))

                # Test with TWO metrics selected
                data = {'metrics': ['foo', 'bar']}
                resp = self.client.post(url, data)
                self.assertEqual(resp.status_code, 302)
                # make sure the metric slug shows up in the redirect URL
                self.assertIn('foo+bar', resp.get("Location", ''))

    def test_aggregate_detail_view(self):
        """Tests ``views.AggregateDetailView``."""
        with patch('redis_metrics.views.get_r') as mock_get_r:
            inst = mock_get_r.return_value
            inst._granularities.return_value = ['daily', 'weekly']

            slug_set = set(['foo', 'bar', 'test-metric', 'yippitty-poo-bah'])
            slugs = '+'.join(slug_set)
            url = reverse('redis_metric_aggregate_detail', args=[slugs])

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('slugs', resp.context_data)
            self.assertIn('granularities', resp.context_data)
            self.assertEqual(resp.context_data['slugs'], slug_set)
            self.assertEqual(resp.context_data['granularities'], ['daily', 'weekly'])

    def _test_aggregate_history_view(self, slugs, granularity):
        """Tests ``views.AggregateHistoryView`` with the given slugs,
        granularity, without a specified date verifying the values are
        correctly passed to the template."""
        with patch('redis_metrics.views.get_r') as mock_get_r:
            inst = mock_get_r.return_value
            inst._granularities.return_value = ['daily', 'weekly']

            slug_set = set(slugs)
            url = reverse('redis_metric_aggregate_history',
                          args=['+'.join(slugs), granularity])

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('slugs', resp.context_data)
            self.assertIn('granularity', resp.context_data)
            self.assertIn('since', resp.context_data)
            self.assertIn('granularities', resp.context_data)
            self.assertEqual(resp.context_data['slugs'], slug_set)
            self.assertEqual(resp.context_data['granularity'], granularity)
            self.assertEqual(resp.context_data['granularities'], ['daily', 'weekly'])
            self.assertIsNone(resp.context_data['since'])

    def test_aggregate_history_view_hourly(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'hourly')

    def test_aggregate_history_view_daily(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'daily')

    def test_aggregate_history_view_weekly(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'weekly')

    def test_aggregate_history_view_monthly(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'monthly')

    def test_aggregate_history_view_yearly(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'yearly')

    def test_aggregate_history_view_since(self):
        """Tests ``views.AggregateHistoryView`` with a ``since`` parameter."""
        slugs = ['foo', 'bar']
        granularity = 'yearly'
        url = reverse(
            'redis_metric_aggregate_history',
            args=['+'.join(slugs), granularity]
        )

        # Do the Request & test results with a just a date
        resp = self.client.get(url, {'since': "2012-12-25"})
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.context_data['since'], datetime)
        self.assertEqual(resp.context_data['since'], datetime(2012, 12, 25))

        # Do the Request & test results with a date & time
        resp = self.client.get(url, {'since': "2012-12-25 11:30:45"})
        self.assertEqual(resp.status_code, 200)
        self.assertIsInstance(resp.context_data['since'], datetime)
        self.assertEqual(
            resp.context_data['since'],
            datetime(2012, 12, 25, 11, 30, 45)
        )

    def test_category_form_view(self):
        """Verifies that GET requests to the ``CategoryFormView`` have the
        correct context info (i.e. a form)."""
        url = reverse('redis_metrics_categorize')
        self.assertUnauthedRequestRedirects(url)

        # NOTE: you can't mock the form in the views, because calls to the
        # form get dispatched somewhere else. That's why this is mocking the
        # R object in the form, instead of the form, itself.
        k = {
            'return_value.metric_slugs.return_value': ['foo', 'bar', 'baz'],
            'return_value._category_slugs.return_value': [],
        }
        with patch('redis_metrics.forms.R', **k):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('form', resp.context_data)
            self.assertIn("id_category_name", str(resp.content))
            self.assertIn("id_metrics", str(resp.content))

    def test_category_form_view_with_initial(self):
        """Verifies that GET requests to the ``CategoryFormView`` have the
        correct context info/initial data when called with a specified
        Category."""
        url = reverse('redis_metrics_categorize', args=['Stuff'])
        self.assertUnauthedRequestRedirects(url)

        # NOTE: you can't mock the form in the views, because calls to the
        # form get dispatched somewhere else. That's why this is mocking the
        # R object in the form, instead of the form, itself.
        k = {
            'return_value.metric_slugs.return_value': ['foo', 'bar', 'baz'],
            'return_value._category_slugs.return_value': ['foo', 'bar'],
        }
        with patch('redis_metrics.forms.R', **k) as mock_R:
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('form', resp.context_data)
            self.assertIn("id_category_name", str(resp.content))
            self.assertIn("id_metrics", str(resp.content))

            # foo and bar should be pre-selected, but baz should not, since
            # it's not in the "Stuff" category
            initial_metrics = resp.context['form'].fields['metrics'].initial
            self.assertIn('foo', initial_metrics)
            self.assertIn('bar', initial_metrics)
            self.assertNotIn('baz', initial_metrics)

            # This is what should happen in the form
            mock_R.assert_has_calls([
                # happens in __init__
                call(),
                call().metric_slugs(),
                call()._category_slugs('Stuff')
            ])

    def test_category_form_view_post(self):
        """Verifies that POST requests to the ``CategoryFormView`` work as
        expected."""
        url = reverse('redis_metrics_categorize')

        # NOTE: you can't mock the form in the views, because calls to the
        # form get dispatched somewhere else. That's why this is mocking the
        # R object in the form, instead of the form, itself.
        k = {
            'return_value.metric_slugs.return_value': ['foo', 'bar', 'baz'],
            'return_value._category_slugs.return_value': ['foo', 'bar'],
        }
        with patch('redis_metrics.forms.R', **k) as mock_R:
            data = {'category_name': 'Foo', 'metrics': ['foo', 'bar']}
            resp = self.client.post(url, data)
            self.assertEqual(resp.status_code, 302)
            # This is what should happen in the form when POSTing
            mock_R.assert_has_calls([
                # happens in __init__
                call(),
                call().metric_slugs(),

                # happens in categorize_metrics
                call().reset_category('Foo', ['foo', 'bar']),
            ])
