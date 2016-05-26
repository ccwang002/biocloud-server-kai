import enum
from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Field, Fieldset, Layout, Submit, HTML
from crispy_forms.bootstrap import FormActions

from core.choices import ChoiceEnum


class AnalysisType(ChoiceEnum):
    RNASeq = _("RNA-Seq Analysis")
    DNASeq = _("DNA-Seq Analysis")


class NewAnalysisTypeSelectionForm(forms.Form):

    analysis_type = forms.ChoiceField(
        choices=AnalysisType.choices(),
        required=True,
        widget=forms.RadioSelect,
        help_text=_("Your desired analysis type.")
    )

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                '',
                Field('analysis_type', placeholder=self.fields['analysis_type'].label),
            ),
            FormActions(
                Submit(
                    'save', _('Create New Analysis'), css_class='btn-lg',
                )
            )
        )
        return helper
