from collections import namedtuple
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView
from django.utils.html import mark_safe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView

from .forms import AbstractAnalysisCreateForm

Pipeline = namedtuple('Pipeline', ['name', 'description', 'url'])

AVAILABLE_PIPELINES = [
    Pipeline(
        'RNA-Seq',
        mark_safe('''This is the description of <strong>RNASeq</strong>'''),
        reverse_lazy('new_rna_seq'),
    ),
]


class SelectNewAnalysisTypeView(LoginRequiredMixin, TemplateView):

    template_name = "analyses/new_analysis_by_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_pipelines'] = AVAILABLE_PIPELINES
        # context['available_pipelines'] = [
        #     str_to_class(*cls.rsplit('.', 1))
        #     for cls in AVAILABLE_PIPELINES
        # ]
        return context


class AbstractAnalysisFormView(LoginRequiredMixin, CreateView):

    form_class = AbstractAnalysisCreateForm
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

