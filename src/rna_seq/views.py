from pipelines.views import AbstractPipelineFormView
from .forms import RNASeqCreateForm


class RNASeqFormView(AbstractPipelineFormView):
    form_class = RNASeqCreateForm
    template_name = 'pipelines/rna_seq.html'
