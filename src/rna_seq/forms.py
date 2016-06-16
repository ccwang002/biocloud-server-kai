from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import InlineField
from crispy_forms.layout import Div, Field, Fieldset, HTML, Layout
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from analyses.forms import (
    AbstractAnalysisCreateForm,
    AnalysisCommonLayout,
    AnalysisFormActions,
    Include,
)
from .models import RNASeqModel


class RNASeqCreateForm(AbstractAnalysisCreateForm):

    class Meta(AbstractAnalysisCreateForm.Meta):
        model = RNASeqModel
        fields = '__all__'
        widgets = {
            **AbstractAnalysisCreateForm.Meta.widgets,
        }

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
            AnalysisFormActions(),
        )
        return helper

