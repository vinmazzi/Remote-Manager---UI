from django.conf.urls import url
from . import views

app_name = 'dhcp'
urlpatterns = [
        url(r'^(?P<group_id>[0-9]+)/options', views.options, name="options"),
        url(r'^(?P<group_id>[0-9]+)/config', views.service_config, name="config"),
        url(r'^(?P<interface_id>[0-9]+)/pool_config', views.pool_config, name="pool_config"),
]
