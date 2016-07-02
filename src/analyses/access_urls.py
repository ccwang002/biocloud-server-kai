from django.conf.urls import url
from .views import canonical_access_report, serve_report

urlpatterns = [
    url(
        r'^report/(?P<report_pk>\d+)/$',
        canonical_access_report,
        name='canonical_access_report',
    ),
    url(
        r'^(?P<auth_key>[\w:-]+)/report/(?P<file_path>.*)$',
        serve_report,
        name='serve_report'
    ),
]
