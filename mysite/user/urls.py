from django.conf.urls import url
from . import views

app_name = 'user'
urlpatterns = [
        url(r'^create$', views.user_create, name="create"),
        url(r'^list$', views.user_list, name="list"),
]
