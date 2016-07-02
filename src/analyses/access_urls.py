from django.conf.urls import url
from .access import canonical_access_report, access_report

urlpatterns = [
    url(
        r'^report/(?P<report_pk>\d+)/$',
        canonical_access_report,
        name='canonical_access_report',
    ),
    url(
        r'^(?P<auth_key>[\w:-]+)/report/(?P<file_path>.*)$',
        access_report,
        name='access_report'
    ),
]
