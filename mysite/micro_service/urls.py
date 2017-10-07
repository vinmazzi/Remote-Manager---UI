from django.conf.urls import url
from . import views

app_name = 'micro_service'
urlpatterns = [
        url(r'^(?P<group_id>[0-9]+)/options', views.options, name="options"),
        url(r'^(?P<group_id>[0-9]+)/list', views.registry_list, name="registry_list"),
        url(r'^(?P<registry_id>[0-9]+)/edit', views.registry_edit, name="registry_edit"),
        url(r'^delete', views.registry_delete, name="registry_delete"),
]
