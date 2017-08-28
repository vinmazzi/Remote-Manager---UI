from django.conf.urls import url
from . import views

app_name = 'network'
urlpatterns = [
        url(r'^(?P<group_id>[0-9]+)/list$', views.network_list, name="list"),
        url(r'^(?P<network_id>[0-9]+)/edit$', views.network_edit, name="edit"),
        url(r'^delete', views.network_delete, name="delete"),
]
