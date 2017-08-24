from django.conf.urls import url
from . import views

app_name = 'login'
urlpatterns = [
        url(r'^$', views.index, name="index"),
        url(r'^login/', views.auth, name="login"),
        url(r'^logout/', views.do_logout, name="logout"),
]
