from django import forms
from django.utils.translation import ugettext_lazy as _


class RequestValidationMixin:
    """Mixin providing ``self._request`` and validation on cleaning.
    """
    error_messages = {
        'no_request': _(
            '{model_name} creation requires a request object.'
        ),
    }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._request = request
        if self._request is None:
            raise forms.ValidationError(self.get_error_message('no_request'))

    def clean(self):
        return self.cleaned_data

    def get_error_message(self, key):
        model_name = self._meta.model.__name__
        return self.error_messages[key].format(
            model_name=model_name,
        )
