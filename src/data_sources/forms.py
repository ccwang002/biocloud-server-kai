from pathlib import Path

from django import forms
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from .models import DataSource


class DataSourceCreateForm(forms.ModelForm):
    class Meta:
        model = DataSource
        fields = [
            'owner', 'file_path', 'checksum',
        ]

    def clean_checksum(self):
        checksum = self.cleaned_data['checksum']
        return checksum.lower()

