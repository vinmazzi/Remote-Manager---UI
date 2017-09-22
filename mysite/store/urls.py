from django.conf.urls import url
from . import views

app_name = 'store'
urlpatterns = [
        url(r'^create$', views.store_create, name="create"),
        url(r'^list$', views.store_list, name="list"),
        url(r'^(?P<store_id>[0-9]+)/edit$', views.store_edit, name="edit"),
        url(r'^(?P<store_id>[0-9]+)/edit_menu$', views.store_edit_menu, name="edit_menu"),
        url(r'^(?P<store_id>[0-9]+)/boxes$', views.store_boxes, name="boxes"),
]
