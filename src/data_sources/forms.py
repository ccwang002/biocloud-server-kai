from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import FormActions
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import modelformset_factory
from django.utils.translation import ugettext_lazy as _

from .models import DataSource


class DataSourceCreateForm(forms.ModelForm):
    class Meta:
        model = DataSource
        fields = [
            'owner', 'file_path',
            'sample_name', 'file_type',
            'metadata', 'checksum',
        ]
        checksum_field = DataSource._meta.get_field('checksum')

    def clean_checksum(self):
        checksum = self.cleaned_data['checksum']
        return checksum.lower()

    def clean(self):
        """Validate the data source existed and has correct checksum.

        The file path has the pattern

        DATA_SOURCES_DIR / owner.pk / file_path
        """
        super().clean()
        if self.errors:
            return  # no owner given, skip rest of the check
        owner = self.cleaned_data['owner']
        file_path = self.cleaned_data['file_path']
        checksum = self.cleaned_data['checksum']

        full_file_path = settings.BIOCLOUD_DATA_SOURCES_DIR.joinpath(
            str(owner.pk), file_path
        )
        # First assert the file path exists
        if not full_file_path.exists():
            raise ValidationError(
                _('Path %(full_file_path)s does not exist'),
                params={'full_file_path': full_file_path},
                code='file_path_not_exist',
            )

        if checksum:
            # A checksum is provided. Check if it matches with the checksum
            # computed from the file content.
            checksum_from_file = self.Meta.checksum_field.checksum_for_file(
                full_file_path
            )
            if checksum != checksum_from_file:
                raise ValidationError(
                    _(
                        'Checksum from input (%(model_checksum)s) mismatches '
                        'with the checksum computed from the file content '
                        '(%(file_checksum)s).'
                    ),
                    params={
                        'model_checksum': checksum,
                        'file_checksum': checksum_from_file,
                    },
                    code='checksum_mismatch',
                )


DataSourceDiscoveryFormSet = modelformset_factory(
    DataSource,
    fields=('file_path', 'sample_name', 'file_type'),
    extra=0
)
DataSourceDiscoveryFormSet.helper = FormHelper()
DataSourceDiscoveryFormSet.helper.template = 'bootstrap/table_inline_formset.html'
DataSourceDiscoveryFormSet.helper.add_input(
    Submit(
        'save', _('Add these data sources'), css_class='btn-lg',
    )
)
