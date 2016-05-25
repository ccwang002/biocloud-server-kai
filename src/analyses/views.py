from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from .forms import NewAnalysisTypeSelectionForm, AnalysisType


class SelectNewAnalysisTypeView(LoginRequiredMixin, FormView):

    form_class = NewAnalysisTypeSelectionForm
    success_url = reverse_lazy("index")
    template_name = "analyses/new_analysis_by_type.html"

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        form = self.get_form()
        if form.is_valid():
            analysis_type = AnalysisType.from_choice(
                form.cleaned_data['analysis_type']
            )
            messages.add_message(
                request, messages.INFO,
                _('You just created a %(analysis_type)s analysis!') % {
                    'analysis_type': analysis_type.name,
                }
            )
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
