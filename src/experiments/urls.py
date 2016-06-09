from django.conf.urls import url

from .views import create_new_experiment

urlpatterns = [
    url(r'^new/$', create_new_experiment,
        name='new_experiment'),
]
