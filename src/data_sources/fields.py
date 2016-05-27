import hashlib
import logging
from django import forms
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

    def __init__(self, *args, blank=False, **kwargs):
        # SHA-256 checksum in hexadecimal representation takes up 64 chars,
        # e.g. 4bit * 64 = 256bit (1 char represents only 4 bit here)
        kwargs['max_length'] = 64
        super().__init__(*args, blank=blank, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        del kwargs['max_length']
        return name, path, args, kwargs

    def formfield(self, **kwargs):
        return super().formfield(**{
            **kwargs,
            'form_class': forms.CharField
        })

    @classmethod
    def get_hash_fun(cls):
        """Return the hash function in use.

        For this field sha256 is used.
        """
        return hashlib.sha256

    @classmethod
    def checksum_for_file(cls, path, chunk_bytes=4 * 2**20):
        """Compute checksum for file

        Args:
            path (pathlib.Path): Compute the checksum at this file path
            chunk_bytes (int): Bytes per chunk for computing the checksum.
                By default is 4MB (= 4 * 2**20).
        """
        hash_fun = cls.get_hash_fun()
        checksum = hash_fun()
        logger.info(
            'Verifying %s checksum of filename %s' %
            (checksum.name, path.name)
        )
        with path.open('rb') as f:
            while True:
                buf = f.read(chunk_bytes)
                if not buf:
                    break  # file ends
                checksum.update(buf)
        logger.info('Checksum verification of filename %s done.' % path.name)
        return checksum.hexdigest()
