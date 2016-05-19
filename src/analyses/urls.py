from django.conf.urls import  url

from .views import (
    SelectNewAnalysisTypeView
)

urlpatterns = [
    url(r'^new/$', SelectNewAnalysisTypeView.as_view(),
        name='new_analysis'),
]
