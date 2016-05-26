from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView

from .forms import AbstractPipelineCreateForm


class AbstractPipelineFormView(LoginRequiredMixin, CreateView):

    form_class = AbstractPipelineCreateForm
    template_name = None

    def get_form_kwargs(self):
        """Pass request object for form creation"""
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs
