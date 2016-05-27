from django.conf.urls import  url

from .views import (
    dashboard_home,
    dashboard_profile_update,
    UserDataSourceListView,
    DiscoverDataSourceListView,
)

urlpatterns = [
    url(r'^$', dashboard_home, name='dashboard_home'),
    url(r'^profile/$', dashboard_profile_update, name='dashboard_profile'),
    url(r'^data-sources/$', UserDataSourceListView.as_view(),
        name='dashboard_data_sources'),
    url(r'^data-sources/discovery/$', DiscoverDataSourceListView.as_view(),
        name='dashboard_discover_data_sources'),
]
