from django.conf.urls import include, url

from .views import (
    SelectNewAnalysisTypeView, SubmittedAnalysisListView,
    update_report
)

urlpatterns = [
    url(r'^new/$', SelectNewAnalysisTypeView.as_view(), name='new_analysis'),
    url(r'^list/$', SubmittedAnalysisListView.as_view(), name='list_analyses'),
    url(r'^update/report/(?P<pk>\d+)/$', update_report, name='update_report'),
    # Hard code all available pipelines
    # To be honest, here we should use a regex to dynamically find the
    # desired analysis and raise 404 when the analysis is not found.
    # But who cares the source code. Huh?
    url(r'^rna-seq/', include('rna_seq.urls')),
]
