from crispy_forms.layout import Div, Field, Fieldset, HTML, Layout
from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django_q.tasks import async

from analyses.forms import (
    AbstractAnalysisCreateForm,
    AnalysisCommonLayout,
    AnalysisFormActions,
    Include,
)
from analyses.models import ExecutionStatus, Report
from .models import RNASeqModel, RNASeqExeDetail


class RNASeqCreateForm(AbstractAnalysisCreateForm):

    class Meta(AbstractAnalysisCreateForm.Meta):
        model = RNASeqModel
        widgets = {
            **AbstractAnalysisCreateForm.Meta.widgets,
        }

    def clean_genome_aligner(self):
        aligner_choice = self.cleaned_data['genome_aligner']
        if aligner_choice.startswith('Tophat'):
            raise forms.ValidationError(_(
                'Tophat aligner is not supported.'
            ))
        return aligner_choice

    def save(self, commit=True):
        job = super().save(commit)
        if commit:
            # Setup execution detail
            RNASeqExeDetail.objects.create(analysis=job)
            # Create new report (for report and result)
            job_report = Report.objects.create()
            job.report = job_report
            job.save(update_fields=['report'])
            # Get the pipeline full url so we can notify the user
            # where to view the result
            job_url = self._request.build_absolute_uri(
                job.get_absolute_url()
            )
            # Submit new task
            async(
                'rna_seq.tasks.run_pipeline',
                job_pk=job.pk,
                job_url=job_url,
            )
            # Mark the analysis is now in queue
            job.execution_status = ExecutionStatus.QUEUEING.name
            job.save(update_fields=['execution_status'])
        return job

    @cached_property
    def helper(self):
        helper = super().helper
        helper.layout = Layout(
            AnalysisCommonLayout(analysis_type="RNA-Seq"),
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
            Fieldset(
                'Genome Alignment',
                Div(
                    Field('genome_aligner', **{"v-model": "aligner"}),
                    Include("rna_seq/_includes/aligner_options.html"),
                    css_id="genome-align-vue",
                    css_class="genome-align-vue",
                ),
            ),
            Fieldset(
                'Expression Quantification and '
                'Differential Expression Analysis',
                HTML(
                    "<p>Use {{ TOOLS_IN_USE.Cufflinks.as_link }} for "
                    "quantifying transcript expression value in RPKM.</p>"
                ),
            ),
            AnalysisFormActions(),
        )
        return helper

