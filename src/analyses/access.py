from pathlib import Path

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect

from .models import Report


@login_required
def canonical_access_report(request, report_pk):
    report_not_found_404 = Http404(
        "Cannot find the given report, or the report does not belong to the "
        "current user."
    )
    try:
        report = Report.objects.get(pk=report_pk)
    except Report.DoesNotExist:
        raise report_not_found_404
    if not report.is_analysis_attached() or \
            report.analysis.owner != request.user:
        raise report_not_found_404
    return redirect(
        access_report, auth_key=report.auth_key, file_path='index.html'
    )


def access_report(request, auth_key, file_path):
    if not file_path:
        return redirect(access_report, auth_key=auth_key, file_path='index.html')
    report_not_found_404 = Http404(
        'Cannot find the given report, or the authentication key is '
        'invalid or expired'
    )
    try:
        report = Report.objects.get_with_auth_key(auth_key)
    except Report.DoesNotExist:
        raise report_not_found_404

    # check if the report is public
    if not report.is_public:
        if report.analysis.owner != request.user:
            return HttpResponseForbidden('The requested report is not public.')

    if settings.DEBUG:
        # use Django debug server
        from django.views.static import serve
        pth = Path(file_path)
        full_dirname = Path(
            settings.BIOCLOUD_REPORTS_DIR, str(report.pk), pth.parent
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


def access_result(request, auth_key, file_path):
    result_not_found_404 = Http404(
        'Cannot find the given result, or the authentication key is '
        'invalid or expired'
    )
    try:
        report = Report.objects.get_with_auth_key(auth_key)
    except Report.DoesNotExist:
        raise result_not_found_404

    # result file must have its path
    if not file_path:
        raise result_not_found_404

    # check if the report is public
    if not report.is_public:
        if report.analysis.owner != request.user:
            return HttpResponseForbidden('The requested result is not public.')

    if settings.DEBUG:
        # use Django debug server
        from django.views.static import serve
        pth = Path(file_path)
        full_dirname = Path(
            settings.BIOCLOUD_RESULTS_DIR, str(report.pk), pth.parent
        )
        return serve(request, pth.name, full_dirname.as_posix())
    else:
        # use nginx
        response = HttpResponse()
        response['Content-Type'] = ''  # let nginx guess mime type
        response['X-Accel-Redirect'] = (
            '/protected/result/%s/%s' % (str(report.pk), file_path)
        )
        return response
