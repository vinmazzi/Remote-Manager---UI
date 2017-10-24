from django.conf.urls import url
from . import views

app_name = 'dnsclient'
urlpatterns = [
        url(r'^(?P<group_id>[0-9]+)edit$', views.dnsclient_edit, name="edit"),
]
