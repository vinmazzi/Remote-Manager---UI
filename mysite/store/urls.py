from django.conf.urls import url
from . import views

app_name = 'store'
urlpatterns = [
        url(r'^(?P<client_id>[0-9]+)/create$', views.store_create, name="create"),
        url(r'^(?P<client_id>[0-9]+)/list$', views.store_list, name="list"),
        url(r'^(?P<store_id>[0-9]+)/edit$', views.store_edit, name="edit"),
        url(r'^(?P<store_id>[0-9]+)/edit_menu$', views.store_edit_menu, name="edit_menu"),
]
