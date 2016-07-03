from django.contrib import messages
from django.contrib.auth import get_user_model

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, TemplateView

from .forms import AbstractAnalysisCreateForm
from .pipelines import AVAILABLE_PIPELINES


User = get_user_model()


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
            _(
                'You just created a %(analysis_type)s analysis! '
                'View its detail <a href="%(analysis_detail_url)s">here</a>.'
            ) % {
                'analysis_type': self.analysis_type,
                'analysis_detail_url': self.object.get_absolute_url(),
            },
            extra_tags='safe',
        )
        return response
