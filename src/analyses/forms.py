import logging
from pathlib import Path

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.forms.utils import ErrorDict
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
import yaml

from core.forms import RequestValidationMixin
from core.utils import setup_yaml
from core.widgets import SimpleMDEWidget
from experiments.models import Experiment
from .models import AbstractAnalysisModel, Report, GenomeReference
from .fields import ExperimentChoiceField
from .form_layouts import AnalysisCommonLayout, AnalysisFormActions, Include

logger = logging.getLogger(__name__)
setup_yaml()


class AbstractAnalysisCreateForm(
    RequestValidationMixin, LoginRequiredMixin, forms.ModelForm
):

    experiment = ExperimentChoiceField(queryset=None)

    class Meta:
        model = AbstractAnalysisModel
        exclude = ('owner', )
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
        """Save the analysis information

        On saving a new analysis, it will:
        1. Fill user field on save.
        2. Create the corresponding result folder
        3. Write the analysis_info.yaml into this folder
           by calling ``pipeline.generate_analysis_info()``
        """
        pipeline = super().save(commit=False)  # type: AbstractAnalysisModel
        pipeline.owner = self._request.user
        if commit:
            pipeline.save()

            # Create the result folder
            pipeline_dir = pipeline.result_dir
            if pipeline_dir.exists():
                logger.warning(
                    'Analysis {} results folder existed at {}. Overwriting...'
                    .format(pipeline.pk, pipeline_dir)
                )
            else:
                pipeline_dir.mkdir()

            # Write analysis_info.yaml into this folder
            analysis_info = pipeline.generate_analysis_info()
            analysis_info_path = pipeline_dir.joinpath('analysis_info.yaml')

            with analysis_info_path.open('w') as f:
                yaml.dump(analysis_info, f, default_flow_style = False)

        return pipeline

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.include_media = False
        helper.layout = Layout(
            AnalysisCommonLayout(analysis_type="Analysis Base"),
            AnalysisFormActions(),
        )
        return helper


class ReportUpdateForm(forms.ModelForm):

    class Meta:
        model = Report
        fields = ('is_public', )

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        helper.form_action = reverse(
            'update_report',
            kwargs={'pk': self.instance.pk}
        )
        return helper


class GenomeReferenceCreateForm(forms.ModelForm):

    class Meta:
        model = GenomeReference
        fields = '__all__'

    def clean_identifier(self):
        """Make sure the folder existed.

        Potentially we can check whether the file structure
        inside this folder follows certain rules here.
        """
        ref_id = self.cleaned_data['identifier']
        ref_dir = Path(settings.BIOCLOUD_REFERENCES_DIR, ref_id)
        if not ref_dir.is_dir():
            raise forms.ValidationError(
                _("Its folder does not exist, expected at %(ref_dir)s"),
                params={'ref_id': ref_id, 'ref_dir': str(ref_dir)}
            )
        return ref_id
