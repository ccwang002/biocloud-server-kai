from django.conf import settings
from django.db import models


# class DataSource(models.Model):
#     """A model to store user's data sources.
#
#     """
#     owner = models.ForeignKey(
#         settings.AUTH_USER_MODEL,
#         on_delete=models.CASCADE,
#         related_name='data_sources',
#     )
#
#     # Don't use FilePathField, not that useful.
#     # Only check file existence at forms
#     file_path = models.CharField(max_length=1023)
#
#     sha256sum
#
#     is_binary
#
