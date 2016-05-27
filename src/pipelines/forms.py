from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.utils import ErrorDict

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

    def check_choice_exists(self):
        if not self.is_bound:
            # No data is bound to form, check the empty form itself
            self._errors = ErrorDict()  # init ErrorDict
            self.cleaned_data = {}  # empty dict so add_error does not fail

    def full_clean(self):
        super().full_clean()
        # BaseForm.full_clean() return immediately if is_bound = True.
        # In our case, we additionally check if specified fields have at least
        # one available choice.
        self.check_choice_exists()

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
