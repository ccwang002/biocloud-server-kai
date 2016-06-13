from django import forms


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
