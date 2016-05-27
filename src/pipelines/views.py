from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
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

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.add_message(
            self.request, messages.INFO,
            _('You just created a %(analysis_type)s analysis!') % {
                'analysis_type': self.object.analysis_type
            }
        )
        return response

