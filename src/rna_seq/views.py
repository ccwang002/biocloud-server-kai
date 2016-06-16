from analyses.views import AbstractAnalysisFormView
from .forms import RNASeqCreateForm


class RNASeqFormView(AbstractAnalysisFormView):
    form_class = RNASeqCreateForm
    template_name = 'rna_seq/rna_seq.html'
