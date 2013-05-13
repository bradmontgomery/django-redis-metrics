#from mock import call, patch, Mock

from django.test import TestCase

from ..forms import AggregateMetricForm, MetricCategoryForm


class TestAggregateMetricForm(TestCase):

    def setUp(self):
        self.form = AggregateMetricForm()

    def test_form(self):
        assert False
        # Test that form has choices populated from R.metric_slugs

    def test_clean(self):
        assert False
        # Verify we get expected results from cleaned_data


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
