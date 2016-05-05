from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _


class SHA256ChecksumField(models.CharField):
    default_validators = [
        RegexValidator(
            regex=r'^[A-Fa-f0-9]{64}$',
            message=_('Invalid SHA256 checksum format'),
            code='invalid_sha256sum',
        ),
    ]
    description = _("SHA256 checksum")

    def __init__(self, blank=False):
        # SHA-256 checksum in hexadecimal representation takes up 64 chars,
        # e.g. 4bit * 64 = 256bit
        super().__init__(blank=blank, max_length=64)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(**{
            **kwargs,
            'form_class': forms.CharField
        })


class DataSource(models.Model):
    """A model to store user's data sources.

    """
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='data_sources',
    )

    # Don't use FilePathField, not that useful.
    # Only check file existence at forms
    file_path = models.CharField(max_length=1023)

    checksum = SHA256ChecksumField(blank=True)

    def __str__(self):
        return (
            '%s/%s (owner: %s)' %
            (self.owner.pk, self.file_path, self.owner.name)
        )
