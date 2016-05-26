from django.views.generic import CreateView
from .forms import AbstractPipelineForm


class AbstractPipelineFormView(CreateView):

    form_class = AbstractPipelineForm
    template_name = None
