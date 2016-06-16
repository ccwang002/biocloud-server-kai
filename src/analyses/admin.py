from django import forms
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from core.widgets import SimpleMDEWidget
from .models import GenomeReference


@admin.register(GenomeReference)
class GenomeReferenceAdmin(admin.ModelAdmin):

    list_display = (
        'organism',
        'identifier',
        'source',
        'newer_reference',
    )
    list_display_links = ['identifier']
    list_filter = (
        'organism', 'source',
    )


class AbstractAnalysisAdminUpdateForm(forms.ModelForm):

    class Meta:
        fields = '__all__'
        widgets = {
            'description': SimpleMDEWidget(),
        }

    @property
    def media(self):
        return super().media + forms.Media(
            css={'all': ['css/tools/simplemde-admin-setup.css']},
            js=['js/tools/simplemde-admin-setup.js'],
        )


class AbstractAnalysisAdmin(admin.ModelAdmin):

    form = AbstractAnalysisAdminUpdateForm
    list_display = (
        "date_created",
        "date_finished",
        "execution_status",
        "name",
        "owner",
        "genome_reference",
        "experiment_name",
    )
    readonly_fields = (
        "date_created",
        "date_finished",
        "execution_status",
    )
    list_display_links = ("name", )

    def experiment_name(self, analysis):
        return analysis.experiment.name
    experiment_name.short_description = 'Experiment'

