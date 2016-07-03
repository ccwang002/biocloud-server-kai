from django.core.urlresolvers import reverse_lazy
from django.utils.html import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView

from analyses import pipelines
from analyses.views import AbstractAnalysisFormView
from .forms import RNASeqCreateForm
from .models import ALL_TOOLS_IN_USE, RNASeqModel


@pipelines.register_view
class RNASeqFormView(AbstractAnalysisFormView):
    form_class = RNASeqCreateForm
    template_name = 'rna_seq/rna_seq.html'
    success_url = reverse_lazy('index')
    analysis_type = _('RNA-Seq')
    analysis_description = mark_safe(
        'This is the description of <strong>RNASeq</strong>'
    )
    analysis_create_url = reverse_lazy('new_rna_seq')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TOOLS_IN_USE'] = ALL_TOOLS_IN_USE.each_per_name
        return context


class RNASeqDetailView(DetailView):
    model = RNASeqModel
    template_name = 'rna_seq/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        analysis = context['object']
        if analysis.report:
            full_report_url = self.request.build_absolute_uri(
                analysis.report.get_absolute_url()
            )
        context.update({
            'analysis': analysis,
            'analysis_detail': analysis.execution_detail,
            'full_report_url': full_report_url
        })
        return context
