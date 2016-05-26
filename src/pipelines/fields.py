from django import forms


class DataSourceModelChoiceField(forms.ModelMultipleChoiceField):

    widget = forms.CheckboxSelectMultiple

    def label_from_instance(self, obj):
        """Modify how the option display of a DataSource object is rendered."""
        return obj.file_path
