from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login
from node.models import Node
from network.models import Network
from network.models import Interface
from group.models import Group
from mysite.utils import Utils
from .forms import DhcpServiceForm
from .forms import DhcpPoolForm
from .models import Dhcp_service
import json, ast
# Create your views here.

def dhcp_service_redis_format(dhcp_service):
   for d in dhcp_service:
       dict_d = model_to_dict(d)
       pop_keys = [ 'group_fk', 'id']

       for key,value in dict_d.items():
           if not value: pop_keys.append(key)
           if ((type(value) is not int) and (len(value.split(',')) > 1)) or (key in ['dnsdomain','ntpservers', 'interfaces']):
               dict_d[key] = value.replace(" ","").split(',')

       for key in pop_keys:
           dict_d.pop(key)

   return json.dumps(dict_d)

def dhcp_pool_redis_format(dhcp_pool):
   pool_hash = {}  
   for d in dhcp_pool:
       dict_d = model_to_dict(d)
       pop_keys = [ 'interface_fk', 'id']

       for key,value in dict_d.items():
           if key == "network_range":
               dict_d.pop(key)
               rvalue = value.replace('-'," ")
               dict_d.update({'range': rvalue})

       for key in pop_keys:
           dict_d.pop(key)
       tmp_pool_name = dict_d['domain'] 
       dict_d.pop('domain')
       tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_pool_name, dict_d))
       pool_hash.update(tmp_format)

   return json.dumps(pool_hash)

def options(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    group = Group.objects.get(pk=group_id)
    return render(request, 'dhcp/group_dhcp_options.html', {'group': group})

def pool_config(request, interface_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    node = Interface.objects.get(pk=interface_id).node_fk
    network = Interface.objects.get(pk=interface_id).network_fk.pk
    interface = Interface.objects.get(pk=interface_id)
    if request.method == 'POST':
        form = DhcpPoolForm(request.POST)
        if form.is_valid():
            if interface.dhcp_pool_set.all():
                pool = interface.dhcp_pool_set.all()[0]
                pool.network_range = form.cleaned_data['network_range']
                pool.network = form.cleaned_data['network']
                pool.domain = form.cleaned_data['domain']
                pool.mask = form.cleaned_data['mask']
                pool.gateway = form.cleaned_data['gateway']
                pool.save()
            else:
                interface.dhcp_pool_set.create(
                          network_range = form.cleaned_data['network_range'],
                          mask = form.cleaned_data['mask'],
                          gateway = form.cleaned_data['gateway'],
                          network = form.cleaned_data['network'],
                          domain = form.cleaned_data['domain'],
                        )
        pools = interface.dhcp_pool_set.all()
        value = dhcp_pool_redis_format(pools)
        key = "{}:{}:dhcp_pools".format(node.client_fk.client_name, node.name)
        Utils.redis_write(key, value)
        return HttpResponseRedirect(reverse('node:edit', kwargs={'node_id':node.pk}))
    if interface.dhcp_pool_set.all():
        pool = interface.dhcp_pool_set.all()[0]
        initial_values = {'domain': pool.domain, 'network': pool.network, 'mask': pool.mask, 'network_range': pool.network_range, 'gateway': pool.gateway}
        form = DhcpPoolForm(initial=initial_values)
    else:
        form = DhcpPoolForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
    return render(request, "dhcp/dhcp_pool.html", {
            "interface_id": interface_id,
            "form": form,
        })


def service_config(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    group = Group.objects.get(pk=group_id)
    if request.method == 'POST':
        form = DhcpServiceForm(request.POST)
        group = Group.objects.get(pk=group_id)
        if form.is_valid():
            if group.dhcp_service_set.all():
                dhcp_service = group.dhcp_service_set.all()[0]
                dhcp_service.nameservers = form.cleaned_data['nameservers']
                dhcp_service.ntpservers = form.cleaned_data['ntpservers']
                dhcp_service.interfaces = form.cleaned_data['interfaces']
                dhcp_service.pxeserver = form.cleaned_data['pxeserver']
                dhcp_service.pxefilename = form.cleaned_data['pxefilename']
                dhcp_service.dnsdomain = form.cleaned_data['dnsdomain']
                dhcp_service.save()
            else:
                Dhcp_service.objects.create(
                          group_fk = group,
                          nameservers = form.cleaned_data['nameservers'],
                          ntpservers = form.cleaned_data['ntpservers'],
                          interfaces = form.cleaned_data['interfaces'],
                          pxeserver  = form.cleaned_data['pxeserver'],
                          pxefilename  = form.cleaned_data['pxefilename'],
                          dnsdomain = form.cleaned_data['dnsdomain']
                        )
            redis_json = dhcp_service_redis_format(group.dhcp_service_set.all())
            redis_key = "{}:{}:dhcp_service".format(group.client_fk.client_name, group.group_name)
            Utils.redis_write(redis_key, redis_json)
    if group.dhcp_service_set.all():
        dhcp = group.dhcp_service_set.all()[0]
        init_hash = {
                'nameservers': dhcp.nameservers,
                'ntpservers': dhcp.ntpservers,
                'interfaces': dhcp.interfaces,
                'pxeserver': dhcp.pxeserver,
                'pxefilename': dhcp.pxefilename,
                'dnsdomain': dhcp.dnsdomain,
            }
        form = DhcpServiceForm(initial=init_hash)
        for field in form.fields:
            if field != "pxeserver":
                form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control tagsinput'})
            else:
                form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        return render(request, 'dhcp/group_dhcp_configure_service.html', {
                'form': form,
                'group_id': group_id,
                'group_name': group.group_name,
            }) 
    else:
        form  = DhcpServiceForm()
        for field in form.fields:
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        return render(request, 'dhcp/group_dhcp_configure_service.html', {
                'form': form,
                'group_id': group_id,
                'group_name': group.group_name,
            }) 
