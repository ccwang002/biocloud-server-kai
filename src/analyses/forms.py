from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorDict
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from core.forms import RequestValidationMixin
from core.widgets import SimpleMDEWidget
from experiments.models import Experiment
from .models import AbstractAnalysisModel
from .fields import ExperimentChoiceField
from .form_layouts import AnalysisCommonLayout


class AbstractAnalysisCreateForm(
    RequestValidationMixin, LoginRequiredMixin, forms.ModelForm
):

    experiment = ExperimentChoiceField(queryset=None)

    class Meta:
        model = AbstractAnalysisModel
        fields = (
            'name', 'description',
        )
        widgets = {
            'description': SimpleMDEWidget(),
        }

    def __init__(self, *args, **kwargs):
        # select owner's data sources
        super().__init__(*args, **kwargs)
        self._current_user_experiments = Experiment.objects.filter(
            owner__exact=self._request.user
        )
        self.fields['experiment'].queryset = self._current_user_experiments

    def check_choice_exists(self):
        if not self.is_bound:
            # No data is bound to form, check the empty form itself
            self._errors = ErrorDict()  # init ErrorDict
            self.cleaned_data = {}  # empty dict so add_error does not fail

        # Check if any experiment exist for this owner
        experiments = self.fields['experiment'].queryset
        if not experiments.exists():
            self.add_error(
                'experiment',
                forms.ValidationError(
                    mark_safe(_(
                        'No experiment is available, so you cannot create a '
                        'new analysis. Try '
                        '<a href="{new_experiment_url}">create one</a> first?'
                    ).format(
                        new_experiment_url=reverse('new_experiment')
                    )),
                )
            )
            # If in future self.add_error('experiment', '...') fails,
            # it can be replaced equivalently by the following code snippets
            # errors = self._errors.setdefault(
            #     'experiment', self.error_class()
            # )
            # errors.append(
            #     forms.ValidationError( ... )
            # )

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

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.layout = Layout(
            AnalysisCommonLayout(analysis_type="Analysis Base"),
            FormActions(
                Submit(
                    'save', _('Create New Analysis'), css_class='btn-lg',
                )
            )
        )
        helper.include_media = False
        return helper

