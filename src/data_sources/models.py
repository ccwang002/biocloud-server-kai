import hashlib
import logging
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import (
    RegexValidator, MinLengthValidator, MaxLengthValidator
)
from django.db import models
from django.utils.translation import ugettext_lazy as _

logger = logging.getLogger(__name__)


class SHA256ChecksumField(models.CharField):
    default_validators = [
        MinLengthValidator(64),
        MaxLengthValidator(64),
        RegexValidator(
            regex=r'^[A-Fa-f0-9]+$',
            message=_(
                'Invalid SHA256 checksum format, expected only '
                'hexadecimal digits'
            ),
            code='sha256sum_non_hexadecimal',
        ),
    ]
    description = _("SHA256 checksum")

    def __init__(self, blank=False):
        # SHA-256 checksum in hexadecimal representation takes up 64 chars,
        # e.g. 4bit * 64 = 256bit (1 char represents only 4 bit here)
        super().__init__(blank=blank, max_length=64)

    @classmethod
    def get_hash_fun(cls):
        """Return the hash function in use.

        For this field sha256 is used.
        """
        return hashlib.sha256

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

    class Meta:
        verbose_name = _('data source')
        verbose_name_plural = _('data sources')
        unique_together = ('owner', 'file_path')

    def __str__(self):
        return (
            '%s/%s (owner: %s)' %
            (self.owner.pk, self.file_path, self.owner.name)
        )

    def get_full_file_path(self):
        full_file_path = settings.BIOCLOUD_DATA_SOURCES_DIR.joinpath(
            str(self.owner.pk), self.file_path
        )
        return full_file_path

    def clean(self):
        """Validate the data source existed and has correct checksum.

        The file path has the pattern

        DATA_SOURCES_DIR / owner.pk / file_path
        """
        self.clean_fields()

        # First assert the file path exists
        full_file_path = self.get_full_file_path()
        if not full_file_path.exists():
            raise ValidationError(
                _('Path %(full_file_path)s dose not exists'),
                params={'full_file_path': full_file_path},
                code='file_path_not_exist',
            )

        if self.checksum:
            # A checksum is provided. Check if it matches with the checksum
            # computed from the file content.
            checksum_from_file = self.checksum_for_file(full_file_path)
            if self.checksum != checksum_from_file:
                raise ValidationError(
                    _(
                        'Checksum from input (%(model_checksum)s) mismatches '
                        'with the checksum computed from the file content '
                        '(%(file_checksum)s).'
                    ),
                    params={
                        'model_checksum': self.checksum,
                        'file_checksum': checksum_from_file,
                    },
                    code='checksum_mismatch',
                )

    @classmethod
    def checksum_for_file(cls, path, chunk_bytes=4 * 2**20):
        """Compute checksum for file

        Args:
            path (pathlib.Path): Compute the checksum at this file path
            chunk_bytes (int): Bytes per chunck for computing the checksum.
                By default is 4MB (= 4 * 2**20).
        """
        hash_fun = cls._meta.get_field('checksum').get_hash_fun()
        checksum = hash_fun()
        logger.info('Verifying %s checksum of filename %s' % (checksum.name, path.name))
        with path.open('rb') as f:
            while True:
                buf = f.read(chunk_bytes)
                if not buf:
                    break  # file ends
                checksum.update(buf)
        logger.info('Checksum verification of filename %s done.' % path.name)
        return checksum.hexdigest()

