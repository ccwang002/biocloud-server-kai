from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, ButtonHolder, Submit
from .models import DataSource


class BaseDataSourceModelForm(forms.ModelForm):

    class Meta:
        model = DataSource
        fields = '__all__'
        checksum_field = DataSource._meta.get_field('checksum')

    def clean_checksum(self):
        checksum = self.cleaned_data['checksum']
        return checksum.lower()

    def get_owner(self):
        return self.cleaned_data['owner']

    def get_file_path(self):
        return self.cleaned_data['file_path']

    def clean(self):
        """Validate the data source existed and has correct checksum.

        The file path has the pattern

        DATA_SOURCES_DIR / owner.pk / file_path
        """
        cleaned_data = super().clean()
        if self.errors:
            return  # no owner given, skip rest of the check
        owner = self.get_owner()
        file_path = self.get_file_path()
        checksum = cleaned_data['checksum']

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


class DataSourceCreateForm(BaseDataSourceModelForm):

    class Meta(BaseDataSourceModelForm.Meta):
        model = DataSource
        fields = [
            'owner', 'file_path',
            'sample_name', 'file_type',
            'checksum', 'metadata',
        ]
        checksum_field = DataSource._meta.get_field('checksum')


class DataSourceUpdateForm(BaseDataSourceModelForm):

    class Meta(BaseDataSourceModelForm.Meta):
        fields = [
            'sample_name', 'file_type',
            'checksum', 'metadata',
        ]

    def get_owner(self):
        return self.instance.owner

    def get_file_path(self):
        return self.instance.file_path

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.form_tag = False
        return helper


class DataSourceDiscoveryForm(DataSourceCreateForm):

    class Meta(DataSourceCreateForm.Meta):
        fields = [
            'file_path',
            'sample_name', 'file_type',
            'checksum', 'metadata',
        ]

    def __init__(self, *args, **kwargs):
        self.owner = kwargs.pop('owner')
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.instance.owner = self.owner
        return super().save(*args, **kwargs)

    def get_owner(self):
        return self.owner


BaseDataSourceFormSet = formset_factory(
    DataSourceDiscoveryForm, extra=0
)


class DataSourceFormSet(BaseDataSourceFormSet):

    @cached_property
    def helper(self):
        helper = FormHelper()
        helper.template = 'bootstrap/table_inline_formset.html'
        helper.layout = Layout(
            Fieldset(
                '',
                Field('file_path'),
                Field('sample_name'),
                Field('file_type'),
                Field('checksum'),
                Field('metadata', type="hidden"),
            )
        )
        helper.add_input(
            Submit(
                'save', _('Add these data sources'), css_class='btn-lg',
            )
        )
        return helper

