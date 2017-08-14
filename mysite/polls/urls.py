from django.conf.urls import url
from . import views

app_name = 'polls'
urlpatterns = [
        url(r'^iptables', views.meuIptables),
        url(r'^teste', views.teste, name='teste'),
        url(r'^$', views.index, name='index'),
        url(r'^specifics/(?P<question_id>[0-9]+)/$', views.detail, name='detail'),
        url(r'^(?P<question_id>[0-9]+)/vote$', views.vote, name='vote'),
        url(r'^(?P<question_id>[0-9]+)/results$', views.results, name='results')
]
