from django.contrib import messages
from django.views.generic import TemplateView

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView

from .forms import AbstractAnalysisCreateForm
from .pipelines import AVAILABLE_PIPELINES


class SelectNewAnalysisTypeView(LoginRequiredMixin, TemplateView):

    template_name = "analyses/new_analysis_by_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_pipelines'] = AVAILABLE_PIPELINES
        return context


class AbstractAnalysisFormView(LoginRequiredMixin, CreateView):

    form_class = AbstractAnalysisCreateForm
    template_name = None
    analysis_type = 'AbstractAnalysis'
    analysis_description = ''
    analysis_create_url = None

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
                'analysis_type': self.analysis_type
            }
        )
        return response
