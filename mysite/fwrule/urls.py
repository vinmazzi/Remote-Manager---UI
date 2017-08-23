from django.conf.urls import url
from . import views

app_name = 'fwrule'
urlpatterns = [
        url(r'^(?P<client_id>[0-9]+)/(?P<group_id>[0-9]+)/fwrules$', views.fwrules, name="fwrules"),
        url(r'^(?P<fwrule_id>[0-9]+)/edit$', views.fwrules_edit, name="fwrules_edit"),
        url(r'^(?P<fwrule_id>[0-9]+)/delete$', views.fwrules_delete, name="fwrules_delete")
]
