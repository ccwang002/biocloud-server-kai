from django.conf.urls import url
from .views import RNASeqFormView, RNASeqDetailView

urlpatterns = [
    url(r'^new/$', RNASeqFormView.as_view(), name='new_rna_seq'),
    url(r'^view/(?P<pk>\d+)/$', RNASeqDetailView.as_view(),
        name='rna_seq_detail'),
]
