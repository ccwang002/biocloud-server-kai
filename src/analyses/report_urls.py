from django.conf.urls import url
from .views import serve_report

urlpatterns = [
    url(
        r'^view/(?P<auth_key>[\w:]+)/(?P<file_path>.*)',
        serve_report,
        name='serve_report'
    ),
]
