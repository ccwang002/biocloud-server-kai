from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, HTML, Layout, Submit
from crispy_forms.bootstrap import FormActions
from django import forms
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.utils.timezone import now

from data_sources.models import FileType
from pipelines.forms import AbstractPipelineCreateForm
from pipelines.fields import DataSourceModelChoiceField
from .models import RNASeqModel


class RNASeqCreateForm(AbstractPipelineCreateForm):

    fastq_sources = DataSourceModelChoiceField(
        label='FASTQ Sources',
        queryset=None,
    )

    class Meta:
        model = RNASeqModel
        fields = (
            *AbstractPipelineCreateForm._meta.fields,
            'fastq_sources',
            'quality_check', 'trim_adapter', 'rm_duplicate',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Select only FASTQ files
        self.fields['fastq_sources'].queryset = (
            self._data_sources.filter(
                file_type=FileType.FASTQ.name
            )
        )

    def check_choice_exists(self):
        super().check_choice_exists()
        # Check if any fastq source exist for this owner
        fastq_sources = self.fields['fastq_sources'].queryset
        if not fastq_sources.exists():
            self.add_error(
                'fastq_sources',
                forms.ValidationError(
                    mark_safe(_(
                        'No available FASTQ sources. Try '
                        '<a href="{dashboard_datasrc_url}">add some</a> first?'
                    ).format(
                        dashboard_datasrc_url=reverse('dashboard_data_sources')
                    )),
                )
            )
            # If in future self.add_error('fastq_source', '...') fails,
            # it can be replaced equivalently by the following code snippets
            # errors = self._errors.setdefault(
            #     'fastq_sources', self.error_class()
            # )
            # errors.append(
            #     forms.ValidationError( ... )
            # )

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
                Field('fastq_sources'),
            ),
            Fieldset(
                'Quality Check',
                HTML(
                    "<p>Examine and process the quality of the sequencing "
                    "reads.</p>"
                ),
                Field('quality_check'),
                Field('trim_adapter'),
                Field('rm_duplicate'),
            ),
            FormActions(
                Submit(
                    'save', _('Create New Analysis'), css_class='btn-lg',
                )
            )
        )
        return helper

