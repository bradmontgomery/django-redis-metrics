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

    def test_form(self):
        """Test that the form has choices from R.metric_slugs, and that
        providing a ``category`` argument sets initial values."""

        # Set up a mock result for R.metric_slugs & R._category_slugs
        config = {
            'return_value.metric_slugs.return_value': ['test-slug'],
            'return_value._category_slugs.return_value': ['test-slug']
        }
        with patch('redis_metrics.forms.R', **config) as mock_R:
            # No Category
            form = MetricCategoryForm()
            self.assertFalse(form.fields['metrics'].required)

            mock_R.assert_has_calls([
                call(),
                call().metric_slugs(),
            ])
            self.assertEqual(
                form.fields['metrics'].choices,
                [('test-slug', 'test-slug')]
            )
            self.assertEqual(form.fields['metrics'].initial, None)
            self.assertEqual(form.fields['category_name'].initial, None)
            self.assertFalse(mock_R._category_slugs.called)
            mock_R.reset_mock()

            # With a Category
            initial = {'category_name': "Sample Category"}
            form = MetricCategoryForm(initial=initial)
            self.assertFalse(form.fields['metrics'].required)

            self.assertEqual(form.fields['metrics'].initial, ['test-slug'])
            self.assertEqual(
                form.fields['category_name'].initial,
                "Sample Category"
            )
            r = mock_R.return_value
            r._category_slugs.assert_called_once_with("Sample Category")

    def test_cleaned_data(self):
        """Verify we get expected results from cleaned_data."""

        # Set up a mock result for R.metric_slugs & R._category_slugs
        config = {
            'return_value.metric_slugs.return_value': ['test-slug'],
            'return_value._category_slugs.return_value': ['test-slug']
        }
        with patch('redis_metrics.forms.R', **config):
            data = {
                'category_name': 'Sample Data',
                'metrics': ['test-slug'],
            }
            form = MetricCategoryForm(data)
            self.assertTrue(form.is_valid())
            self.assertEqual(form.cleaned_data, data)

    def test_categorize_metrics(self):
        """Test the ``categorize_metrics`` method; This method should be called
        after POSTing."""
        k = {
            'return_value.metric_slugs.return_value': ['foo', 'bar', 'baz'],
            'return_value._category_slugs.return_value': ['foo', 'bar'],
        }
        with patch('redis_metrics.forms.R', **k) as mock_R:
            data = {'category_name': 'Foo', 'metrics': ['foo', 'bar']}
            form = MetricCategoryForm(data)
            self.assertTrue(form.is_valid())
            form.categorize_metrics()
            # This is what should happen in the form when POSTing
            mock_R.assert_has_calls([
                # happens in __init__
                call(),
                call().metric_slugs(),

                # happens in categorize_metrics
                call().reset_category('Foo', ['foo', 'bar'])
            ])
