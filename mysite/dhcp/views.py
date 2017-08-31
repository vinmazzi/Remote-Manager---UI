from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login
from group.models import Group
from mysite.utils import Utils
from .forms import DhcpServiceForm
from .models import Dhcp_service
import json
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

def options(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    group = Group.objects.get(pk=group_id)
    return render(request, 'dhcp/group_dhcp_options.html', {'group': group})

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
