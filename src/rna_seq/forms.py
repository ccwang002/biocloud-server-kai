from crispy_forms.layout import Div, Field, Fieldset, HTML, Layout
from django.utils.functional import cached_property
from django_q.tasks import async

from analyses.forms import (
    AbstractAnalysisCreateForm,
    AnalysisCommonLayout,
    AnalysisFormActions,
    Include,
)
from analyses.models import ExecutionStatus
from .models import RNASeqModel, RNASeqExeDetail


class RNASeqCreateForm(AbstractAnalysisCreateForm):

    class Meta(AbstractAnalysisCreateForm.Meta):
        model = RNASeqModel
        widgets = {
            **AbstractAnalysisCreateForm.Meta.widgets,
        }

    def save(self, commit=True):
        pipeline = super().save(commit)
        if commit:
            # Setup execution detail
            pipeline_detail = RNASeqExeDetail.objects.create(
                analysis=pipeline
            )
            # Get the pipeline full url so we can notify the user
            # where to view the result
            pipeline_url = self._request.build_absolute_uri(
                pipeline.get_absolute_url()
            )
            # Submit new task
            async(
                'rna_seq.tasks.run_pipeline',
                pipeline_pk=pipeline.pk,
                pipeline_url=pipeline_url,
            )
            # Mark the analysis is now in queue
            pipeline.execution_status = ExecutionStatus.QUEUEING.name
            pipeline.save()
        return pipeline

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

