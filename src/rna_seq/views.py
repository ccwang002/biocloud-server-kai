from analyses.views import AbstractAnalysisFormView
from .forms import RNASeqCreateForm

from .models import ALL_TOOLS_IN_USE


class RNASeqFormView(AbstractAnalysisFormView):
    form_class = RNASeqCreateForm
    template_name = 'rna_seq/rna_seq.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['TOOLS_IN_USE'] = ALL_TOOLS_IN_USE.each_per_name
        return context
