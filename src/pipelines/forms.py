from django import forms
from .models import AbstractPipelineModel


class AbstractPipelineForm(forms.ModelForm):

    class Meta:
        model = AbstractPipelineModel
        fields = (
            'analysis_name',
        )
