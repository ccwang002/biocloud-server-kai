from collections import namedtuple
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic import FormView, TemplateView
from django.utils.html import mark_safe


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
