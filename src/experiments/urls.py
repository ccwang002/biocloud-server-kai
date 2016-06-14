from django.conf.urls import url

from .views import (
    create_new_experiment,
    ExperimentListView,
    ExperimentDetailView,
)

urlpatterns = [
    url(r'^$', ExperimentListView.as_view(), name='list_experiment'),
    url(r'^new/$', create_new_experiment, name='new_experiment'),
    url(
        r'^view/(?P<pk>\d+)/$',
        ExperimentDetailView.as_view(),
        name='detail_experiment',
    ),
]
