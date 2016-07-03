from django import forms
from django.db import models
from analyses.models import StageStatus


class ExperimentChoiceField(forms.ModelChoiceField):

    widget = forms.Select

    def label_from_instance(self, experiment):
        """Option display label of a Experiment object.

        """
        return (
            '{name:s} '
            '(Conditions: {conditions:s}) '
            'created at {date_created:%Y-%m-%d} UTC'
            .format(
                name=experiment.name,
                conditions=', '.join(experiment.condition_names),
                date_created=experiment.date_created,
            )
        )


class StageStatusField(models.CharField):

    def __init__(self, *args, **kwargs):
        kwargs.update({
            'choices': StageStatus.choices(),
            'max_length': 32,
            'default': StageStatus.WAITING.name,
        })
        super().__init__(*args, **kwargs)
