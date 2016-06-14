from django import forms
from django.contrib import admin

from core.widgets import SimpleMDEWidget
from .models import Experiment, Condition


class ConditionInline(admin.TabularInline):
    model = Experiment.data_sources.through
    ordering = ("experiment", "condition", "sample_name", "data_source")
    raw_id_fields = ("data_source", )
    extra = 0


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
        return (
            '{name:s} was created by {owner:s} involving '
            '{num_sources:d} data sources. '
            'It defined {num_sample:d} samples: {samples:s}, '
            'and defined {num_condition:d} conditions: {conditions:s}.'
            .format(
                owner=experiment.owner.name,
                name=experiment.name,
                num_sample=len(experiment.sample_names),
                samples=', '.join(experiment.sample_names),
                num_sources=experiment.conditions.count(),
                conditions=', '.join(experiment.condition_names),
                num_condition=len(experiment.condition_names),
            )
        )
    summarize_experiment.short_description = 'Summary'

