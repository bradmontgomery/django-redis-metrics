"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from mock import call, patch

try:
    # Django 1.5
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:
    # Fallback for Django 1.4 (or lower)
    from django.contrib.auth.models import User

from django.core.urlresolvers import reverse
from django.test import TestCase, Client


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
                call.get_metric_history(
                    since=None,
                    slugs=slug,
                    granularity=granularity
                )
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

    def test_aggregate_form_view(self):
        """Verifies that GET requests to the ``AggregateFormView`` have the
        correct context info (i.e. a form)."""
        url = reverse('redis_metric_aggregate')
        self.assertUnauthedRequestRedirects(url)
        with patch('redis_metrics.views.R'):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('form', resp.context_data)

    def test_aggregate_form_view_post(self):
        """Verifies that POST requests to the ``AggregateFormView`` work as
        expected."""
        url = reverse('redis_metric_aggregate')
        with patch('redis_metrics.views.R'):
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

        slug_set = set(['foo', 'bar', 'test-metric', 'yippitty-poo-bah'])
        slugs = '+'.join(slug_set)
        url = reverse('redis_metric_aggregate_detail', args=[slugs])

        with patch('redis_metrics.views.R') as mock_r:
            # Set up a return value for ``R.get_metric(slug)``
            r = mock_r.return_value  # Get an instance of our Mocked R class
            metric_list = []
            for slug in slug_set:
                metric_list.append((slug, {
                        'day': '1',
                        'month': '22',
                        'week': '333',
                        'year': '4444'
                    })
                )
            r.get_metric.return_value = metric_list

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('slugs', resp.context_data)
            self.assertIn('metrics', resp.context_data)
            self.assertEqual(resp.context_data['slugs'], slug_set)

            # Make sure our Mocked R instance had its ``get_metrics`` method
            # called with the correct parameter
            r.assert_has_calls([call.get_metrics(slug_set)])

    def _metrichistory(self, slugs, granularity):
        """Create an appropriate return value for ``R.get_metric_history``
        based on the given slugs and granularity."""
        history = []
        value = 0
        for slug in slugs:
            if granularity == "daily":
                key_pattern = "m:{0}:2013-01-10"
            elif granularity == "weekly":
                key_pattern = "m:{0}:w:2013-01"
            elif granularity == "monthly":
                key_pattern = "m:{0}:m:2013-01"
            elif granularity == "yearly":
                key_pattern = "m:{0}:y:2013"

            history.append((key_pattern.format(slug), value))
            value += 1
        return history

    def _test_aggregate_history_view(self, slugs, granularity):
        """Tests ``views.AggregateHistoryView`` with the given slugs and
        granularity (i.e. 'daily', 'weekly', 'monthly', 'yearly')."""
        slug_set = set(slugs)
        url = reverse('redis_metric_aggregate_history',
                      args=['+'.join(slugs), granularity])

        with patch('redis_metrics.views.R') as mock_r:
            # Set up a return value for ``get_metric_history_as_columns``
            r = mock_r.return_value  # Get an instance of our Mocked R class
            r.get_metric_history.return_value = self._metrichistory(
                slugs, granularity)

            # Do the Request & test results
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('slugs', resp.context_data)
            self.assertIn('granularity', resp.context_data)
            self.assertIn('metric_history', resp.context_data)
            self.assertEqual(resp.context_data['slugs'], slug_set)
            self.assertEqual(resp.context_data['granularity'], granularity)

            # Make sure our Mocked R instance had its
            # ``get_metric_history_as_columns`` method called with the correct
            # parameters
            c = call.get_metric_history_as_columns(
                slugs=slugs,
                granularity=granularity
            )
            r.assert_has_calls([c])

    def test_aggregate_history_view_daily(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'daily')

    def test_aggregate_history_view_weekly(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'weekly')

    def test_aggregate_history_view_monthly(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'monthly')

    def test_aggregate_history_view_yearly(self):
        self._test_aggregate_history_view(['foo', 'bar'], 'yearly')
