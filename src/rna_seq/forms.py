from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, Submit
from crispy_forms.bootstrap import FormActions
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from pipelines.forms import AbstractPipelineCreateForm
from .models import RNASeqModel


class RNASeqCreateForm(AbstractPipelineCreateForm):

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                '',
                Field(
                    'analysis_name',
                    placeholder=self.fields['analysis_name'].label
                ),
            ),
            FormActions(
                Submit(
                    'save', _('Create New Analysis'), css_class='btn-lg',
                )
            )
        )
        return helper

    class Meta:
        model = RNASeqModel
        fields = ('analysis_name', )
