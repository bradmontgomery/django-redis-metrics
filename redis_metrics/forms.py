from __future__ import unicode_literals
from django import forms
from .models import R


class AggregateMetricForm(forms.Form):
    metrics = forms.MultipleChoiceField(
        choices=[],
        widget=forms.widgets.CheckboxSelectMultiple(),
    )

    def __init__(self, *args, **kwargs):
        super(AggregateMetricForm, self).__init__(*args, **kwargs)
        r = R()
        choices = [(slug, slug) for slug in r.metric_slugs()]
        self.fields['metrics'].choices = choices


class MetricCategoryForm(forms.Form):
    category_name = forms.CharField()
    metrics = forms.MultipleChoiceField(
        choices=[],
        widget=forms.widgets.CheckboxSelectMultiple(),
        required=False  # Don't require this, unchecking all metrics will
                        # remove a Category from Redis.
    )

    def __init__(self, *args, **kwargs):
        """See if this form is created with an initial Category. If so, we call
        out to ``R._category_slugs`` to find the pre-selected metrics. Any
        initial data should look like this:

            {'category_name': 'Whatever'}


        """
        super(MetricCategoryForm, self).__init__(*args, **kwargs)
        self.r = R()  # Keep a connection to our Redis wrapper
        # The list of available choices should include all metrics
        choices = [(slug, slug) for slug in self.r.metric_slugs()]
        self.fields['metrics'].choices = choices

        # If a "category" is provided, set inital values (pre-selected)
        initial = kwargs.get('initial', None)
        if initial and 'category_name' in initial:
            category = initial['category_name']
            self.fields['category_name'].initial = category
            self.fields['metrics'].initial = self.r._category_slugs(category)

    def categorize_metrics(self):
        """Called only on a valid form, this method will place the chosen
        metrics in the given catgory."""
        category = self.cleaned_data['category_name']
        metrics = self.cleaned_data['metrics']
        self.r.reset_category(category, metrics)
