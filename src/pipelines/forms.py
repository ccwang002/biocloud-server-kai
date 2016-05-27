from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin

from core.forms import RequestValidationMixin
from data_sources.models import DataSource
from .models import AbstractPipelineModel


class AbstractPipelineCreateForm(
    RequestValidationMixin, LoginRequiredMixin, forms.ModelForm
):

    def __init__(self, *args, **kwargs):
        # select owner's data sources
        super().__init__(*args, **kwargs)
        self._data_sources = DataSource.objects.filter(
            owner__exact=self._request.user
        )


    def save(self, commit=True):
        """Fill user field on save.
        """
        pipeline = super().save(commit=False)
        pipeline.owner = self._request.user
        if commit:
            pipeline.save()
        return pipeline

    class Meta:
        model = AbstractPipelineModel
        fields = (
            'analysis_name',
        )
