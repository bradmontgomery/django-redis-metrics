from django import forms
from django.template.defaultfilters import slugify

from .models import R

class AggregateMetricForm(forms.Form):
    metrics = forms.MultipleChoiceField(choices=[])

    def __init__(self, *args, **kwargs):
        super(AggregateMetricForm, self).__init__(*args, **kwargs)
        r = R()
        choices = [(slug, slug) for slug in r.metric_slugs()]
        self.fields['metrics'].choices = choices
