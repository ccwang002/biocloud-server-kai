from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, HTML, Layout, Submit
from django.utils.functional import cached_property
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

from analyses.forms import AbstractAnalysisCreateForm
from .models import RNASeqModel


class RNASeqCreateForm(AbstractAnalysisCreateForm):

    class Meta(AbstractAnalysisCreateForm.Meta):
        model = RNASeqModel
        fields = (
            *AbstractAnalysisCreateForm.Meta.fields,
            'quality_check', 'trim_adapter', 'rm_duplicate',
        )
        widgets = {
            **AbstractAnalysisCreateForm.Meta.widgets,
        }

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                'Analysis description',
                Field(
                    'name',
                    value='RNA-Seq {:%Y-%m-%d %H:%M}'.format(now())
                ),
                Field('description'),
            ),
            Fieldset(
                'Samples and Conditions',
                HTML("<p>Specify your experiment here.</p>"),
                Field('experiment'),
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
        helper.include_media = False
        return helper

