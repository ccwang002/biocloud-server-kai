from django import forms
from django.contrib import admin

from core.widgets import SimpleMDEWidget
from .models import Experiment, Condition


class ConditionInline(admin.TabularInline):
    model = Experiment.data_sources.through


class ExperimentAdminForm(forms.ModelForm):

    class Meta:
        model = Experiment
        fields = ['owner', 'name', 'description']
        widgets = {
            'description': SimpleMDEWidget,
        }

    @property
    def media(self):
        return super().media + forms.Media(
            css={'all': ['css/tools/simplemde-admin-setup.css']},
            js=['js/tools/simplemde-admin-setup.js'],
        )


@admin.register(Experiment)
class ExperimentAdmin(admin.ModelAdmin):

    form = ExperimentAdminForm
    list_display = [
        'pk',
        'name',
        'owner',
        'date_created',
        'summarize_experiment',
    ]
    list_display_links = [
        'name',
    ]
    inlines = [
        ConditionInline,
    ]
    exclude = [
        'data_sources',
    ]

    def summarize_experiment(self, experiment):
        return str(experiment)
    summarize_experiment.short_description = 'Summary'

