from django.conf.urls import url
from .views import canonical_access_report

urlpatterns = [
    url(
        r'^report/(?P<report_pk>\d+)/$',
        canonical_access_report,
        name='canonical_access_report',
    ),
]
