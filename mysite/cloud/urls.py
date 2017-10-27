from django.conf.urls import url
from . import views

app_name = 'cloud'
urlpatterns = [
        url(r'^options', views.cloud_options, name="options"),
        url(r'^vpc/list', views.vpc_list, name="vpc_list"),
        url(r'^vpc/delete', views.vpc_delete, name="vpc_delete"),
        url(r'^vpc/(?P<vpc_id>[0-9]+)/vpc_edit', views.vpc_edit, name="vpc_edit"),
        url(r'^subnet/list', views.subnet_list, name="subnet_list"),
        url(r'^subnet/delete', views.subnet_delete, name="subnet_delete"),
        url(r'^subnet/(?P<subnet_id>[0-9]+)/subnet_edit', views.subnet_edit, name="subnet_edit"),
        url(r'^fwrule/group/list', views.fwrule_group_list, name="fwrule_group_list"),
        url(r'^fwrule/group/(?P<sg_id>[0-9]+)/edit', views.fwrule_group_edit, name="fwrule_group_edit"),
        url(r'^fwrule/group/rules/(?P<sg_id>[0-9]+)/edit', views.fwrule_group_rule_edit, name="fwrule_group_rule_edit"),
]
