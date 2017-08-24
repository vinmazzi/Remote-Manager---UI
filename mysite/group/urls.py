from django.conf.urls import url
from . import views

app_name = 'group'
urlpatterns = [
        url(r'^teste$', views.teste, name="teste"),
        url(r'^(?P<client_id>[0-9]+)/group$', views.group, name="index"),
        url(r'^(?P<client_id>[0-9]+)/create$', views.group_create, name="create"),
        url(r'^(?P<client_id>[0-9]+)/list_config$', views.group_list_config, name="list_config"),
        url(r'^(?P<group_id>[0-9]+)/config$', views.group_config, name="config"),
]
