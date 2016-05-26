from pipelines.views import AbstractPipelineFormView
from .forms import RNASeqForm


class RNASeqFormView(AbstractPipelineFormView):
    form_class = RNASeqForm
    template_name = 'pipelines/rna_seq.html'
