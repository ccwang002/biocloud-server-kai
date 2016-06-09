from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Fieldset, Layout, Submit, Div
from django import forms
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _

from core.widgets import SimpleMDEWidget
from .models import Experiment, Condition


class ExperimentCreateForm(forms.ModelForm):

    class Meta:
        model = Experiment
        fields = ['name', 'description']
        widgets = {
            'description': SimpleMDEWidget(),
        }

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            Fieldset(
                '',
                'name',
                'description',
            ),
        )
        return helper
