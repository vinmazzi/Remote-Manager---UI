from django.conf.urls import url
from . import views

app_name = 'ntp'
urlpatterns = [
        url(r'^(?P<group_id>[0-9]+)/edit', views.ntp_edit, name="edit"),
]
