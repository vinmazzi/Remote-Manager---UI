from django.conf.urls import url
from . import views

app_name = 'node'
urlpatterns = [
        url(r'^(?P<client_id>[0-9]+)/list$', views.node_list, name="list"),
        url(r'^(?P<client_id>[0-9]+)/discovery$', views.discovery_node, name="discovery"),
]

