from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, TemplateView

from .forms import AbstractAnalysisCreateForm
from .models import Report
from .pipelines import AVAILABLE_PIPELINES


User = get_user_model()


def serve_report(request, auth_key, file_path):
    if not file_path:
        return redirect(serve_report, auth_key=auth_key, file_path='index.html')
    report_not_found_404 = Http404(
        'Cannot found the given report, or the authentication key is '
        'invalid or expired'
    )
    try:
        report = Report.objects.get_with_auth_key(auth_key)
    except Report.DoesNotExist:
        raise report_not_found_404
    if settings.DEBUG:
        # use Django debug server
        from django.views.static import serve
        pth = Path(file_path)
        full_dirname = Path(
            settings.BIOCLOUD_REPORT_DIR, str(report.pk), pth.parent
        )
        return serve(request, pth.name, full_dirname.as_posix())
    else:
        # use nginx
        response = HttpResponse()
        response['Content-Type'] = ''  # let nginx guess mime type
        response['X-Accel-Redirect'] = (
            '/protected/report/%s/%s' % (str(report.pk), file_path)
        )
        return response


class SelectNewAnalysisTypeView(LoginRequiredMixin, TemplateView):

    template_name = "analyses/new_analysis_by_type.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_pipelines'] = AVAILABLE_PIPELINES
        return context


class AbstractAnalysisFormView(LoginRequiredMixin, CreateView):

    form_class = AbstractAnalysisCreateForm
    template_name = None
    analysis_type = 'AbstractAnalysis'
    analysis_description = ''
    analysis_create_url = None

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
                'analysis_type': self.analysis_type
            }
        )
        return response
