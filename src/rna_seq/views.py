from django.core.urlresolvers import reverse_lazy

from analyses.views import AbstractAnalysisFormView
from .forms import RNASeqCreateForm
from .models import ALL_TOOLS_IN_USE


class RNASeqFormView(AbstractAnalysisFormView):
    form_class = RNASeqCreateForm
    analysis_type = "RNA-Seq"
    template_name = 'rna_seq/rna_seq.html'
    success_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TOOLS_IN_USE'] = ALL_TOOLS_IN_USE.each_per_name
        return context
