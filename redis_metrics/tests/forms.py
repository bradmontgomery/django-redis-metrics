from mock import call, patch
from django.test import TestCase

from ..forms import AggregateMetricForm, MetricCategoryForm


class TestAggregateMetricForm(TestCase):

    def test_form(self):
        """Test that form has choices populated from R.metric_slugs"""
        # Set up a mock result for R.metric_slugs
        config = {'return_value.metric_slugs.return_value': ['test-slug']}
        with patch('redis_metrics.forms.R', **config) as mock_R:
            form = AggregateMetricForm()
            mock_R.assert_has_calls([
                call(),
                call().metric_slugs(),
            ])
            self.assertEqual(
                form.fields['metrics'].choices,
                [('test-slug', 'test-slug')]
            )

    def test_cleaned_data(self):
        """Verify we get expected results from cleaned_data"""
        # Set up a mock result for R.metric_slugs
        config = {'return_value.metric_slugs.return_value': ['test-slug']}
        with patch('redis_metrics.forms.R', **config):
            form = AggregateMetricForm({"metrics": ["test-slug"]})
            self.assertTrue(form.is_valid())
            self.assertEqual(form.cleaned_data, {"metrics": ["test-slug"]})


class TestMetricCategoryForm(TestCase):

    def setUp(self):
        self.form = MetricCategoryForm()

    def test_form(self):
        assert False
        # Test that the form has choices from R.metric_slugs, and that
        # providing a ``category`` argument sets initial values

    def test_clean(self):
        assert False
        # Verify we get expected results from cleaned_data
