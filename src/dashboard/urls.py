from django.conf.urls import url

from .views import dashboard_home, dashboard_profile_update


urlpatterns = [
    url(r'^$', dashboard_home, name='dashboard_home'),
    url(r'^profile/$', dashboard_profile_update, name='dashboard_profile'),
]
