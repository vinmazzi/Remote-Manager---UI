from django.conf.urls import url
from . import views

urlpatterns = [
        url(r'^iptables', views.meuIptables),
        url(r'^teste', views.teste, name='teste'),
        url(r'^$', views.index, name='index'),
        url(r'specifics/(?P<question_id>[0-9]+)/$', views.detail, name='details')
]
