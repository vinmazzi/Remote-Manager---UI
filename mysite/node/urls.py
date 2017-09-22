from django.conf.urls import url
from . import views

app_name = 'node'
urlpatterns = [
        url(r'^list$', views.node_list, name="list"),
        url(r'^(?P<store_id>[0-9]+)/create$', views.node_create, name="create"),
        url(r'^(?P<node_id>[0-9]+)/edit$', views.node_edit, name="edit"),
]
