from django.conf.urls import url
from . import views

app_name = 'group'
urlpatterns = [
        url(r'^group$', views.group, name="index"),
        url(r'^create$', views.group_create, name="create"),
        url(r'^list_config$', views.group_list_config, name="list_config"),
        url(r'^(?P<group_id>[0-9]+)/config$', views.group_config, name="config"),
]
