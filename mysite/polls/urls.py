from django.conf.urls import url
from . import views

urlpatterns = [
        url(r'^iptable?', views.meuIptables),
        url(r'^teste', views.teste, name='teste'),
        url(r'^$', views.index, name='index'),
]
