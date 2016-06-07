from django.conf.urls import url

from .views import (
    UserDataSourceListView,
    UserDataSourceUpdateView,
    discover_data_source,
)

urlpatterns = [
    url(r'^$', UserDataSourceListView.as_view(),
        name='data_sources'),
    url(r'^discovery/$', discover_data_source,
        name='discover_data_sources'),
    url(r'update/(?P<pk>\d+)', UserDataSourceUpdateView.as_view(),
        name='update_data_source')
]
