from django.conf.urls import url

from .views import (
    create_new_experiment,
    get_experiment_info_json,
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
    url(
        r'^fetch/info/$',
        get_experiment_info_json,
        name='ajax_experiment_info',
    )
]
