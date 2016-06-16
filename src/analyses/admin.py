from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import GenomeReference


@admin.register(GenomeReference)
class GenomeReferenceAdmin(admin.ModelAdmin):

    fields = (
        'organism',
        'identifier',
        'source',
        'newer_reference',
    )
    list_display = (
        'organism',
        'identifier',
        'source',
        'newer_reference',
    )
    ordering = (
        'organism', '-identifier'
    )
    list_display_links = ['identifier']
    list_filter = (
        'organism', 'source',
    )
