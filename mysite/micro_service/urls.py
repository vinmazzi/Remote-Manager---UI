from django.conf.urls import url
from . import views

app_name = 'micro_service'
urlpatterns = [
        url(r'^(?P<group_id>[0-9]+)/options', views.options, name="options"),
        url(r'^(?P<group_id>[0-9]+)/list', views.registry_list, name="registry_list"),
        url(r'^(?P<registry_id>[0-9]+)/edit', views.registry_edit, name="registry_edit"),
        url(r'^(?P<container_id>[0-9]+)/container_edit', views.container_edit, name="container_edit"),
        url(r'^(?P<group_id>[0-9]+)/catalog_list', views.catalog_list, name="catalog_list"),
        url(r'^catalog_delete', views.catalog_container_delete, name="catalog_delete"),
        url(r'^delete', views.registry_delete, name="registry_delete"),
]
