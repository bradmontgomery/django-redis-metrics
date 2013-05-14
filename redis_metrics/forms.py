from django import forms
from .models import R


class AggregateMetricForm(forms.Form):
    metrics = forms.MultipleChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(AggregateMetricForm, self).__init__(*args, **kwargs)
        r = R()
        choices = [(slug, slug) for slug in r.metric_slugs()]
        self.fields['metrics'].choices = choices


class MetricCategoryForm(forms.Form):
    category_name = forms.CharField()
    metrics = forms.MultipleChoiceField(
        choices=[],
        widget=forms.widgets.CheckboxSelectMultiple()
    )

    def __init__(self, *args, **kwargs):
        self.r = R()  # Keep a connection to our Redis wrapper
        category = kwargs.get('category', None)
        if category:
            del kwargs['category']

        super(MetricCategoryForm, self).__init__(*args, **kwargs)
        # The list of available choices should include all metrics
        choices = [(slug, slug) for slug in self.r.metric_slugs()]
        self.fields['metrics'].choices = choices

        # If a "category" is provided, set inital values (pre-selected)
        if category:
            self.fields['category_name'].initial = category
            self.fields['metrics'].initial = self.r._category_slugs(category)

    def categorize_metrics(self):
        """Called only on a valid form, this method will place the chosen
        metrics in the given catgory."""
        for metric in self.cleaned_data['metrics']:
            self.r._categorize(metric, self.cleaned_data['category_name'])
