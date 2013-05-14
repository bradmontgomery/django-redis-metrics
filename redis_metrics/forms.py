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
        category = kwargs.get('category', None)
        if category:
            del kwargs['category']

        super(MetricCategoryForm, self).__init__(*args, **kwargs)
        r = R()
        # The list of available choices should include all metrics
        choices = [(slug, slug) for slug in r.metric_slugs()]
        self.fields['metrics'].choices = choices

        # If a "category" is provided, set inital values (pre-selected)
        if category:
            self.fields['category_name'].initial = category
            self.fields['metrics'].initial = r._category_slugs(category)
