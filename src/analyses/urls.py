from django.conf.urls import  url

from .views import (
    SelectNewAnalysisTypeView,
)
from rna_seq.views import RNASeqFormView

urlpatterns = [
    url(r'^new/$', SelectNewAnalysisTypeView.as_view(), name='new_analysis'),
    # Hard code all available pipelines
    # To be honest, here we should use a regex to dynamically find the
    # desired analysis and raise 404 when the analysis is not found.
    # But who cares the source code. Huh?
    url(r'^new/rna-seq/$', RNASeqFormView.as_view(), name='new_rna_seq'),
]
