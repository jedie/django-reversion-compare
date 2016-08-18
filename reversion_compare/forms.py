"""Forms for django-reversion."""

from django import forms


class SelectDiffForm(forms.Form):
    version_id1 = forms.IntegerField(min_value=1)
    version_id2 = forms.IntegerField(min_value=1)
