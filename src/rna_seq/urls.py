from django.conf.urls import url
from .views import RNASeqFormView

urlpatterns = [
    url(r'^$', RNASeqFormView.as_view(), name='new_rna_seq'),
]
