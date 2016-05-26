from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, HTML, Layout, Submit
from crispy_forms.bootstrap import FormActions
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from pipelines.forms import AbstractPipelineCreateForm
from pipelines.fields import DataSourceModelChoiceField
from .models import RNASeqModel


class RNASeqCreateForm(AbstractPipelineCreateForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fastq_sources'].queryset = self._data_sources

    fastq_sources = DataSourceModelChoiceField(
        label='FASTQ Sources',
        queryset=None,
    )

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                'Analysis description',
                Field(
                    'analysis_name',
                    value='RNA-Seq {:%Y-%m-%d %H:%M}'.format(now())
                ),
            ),
            Fieldset(
                'Data Sources',
                HTML("<p>Specifiy your input FASTQ sources here.</p>"),
                Field(
                    'fastq_sources',
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
        fields = (
            *AbstractPipelineCreateForm._meta.fields,
            'fastq_sources'
        )
