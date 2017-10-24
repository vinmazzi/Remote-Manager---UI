from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from group.models import Group
from mysite.utils import Utils
from .models import DnsClient
from .forms import DnsClientForm
import json
# Create your views here.

def dnsclient_redis_format(dnsclient):
    if dnsclient.dns2_address:
        dnsclient_hash = {
                    'nameservers': [dnsclient.dns1_address, dnsclient.dns2_address],
                    'domainname': dnsclient.domain,
                }
    else:
        dnsclient_hash = {
                    'nameservers': [dnsclient.dns1_address],
                    'domainname': dnsclient.domain,
                }
    return json.dumps(dnsclient_hash)



def dnsclient_edit(request, group_id):
    group = Group.objects.get(pk=group_id)
    if request.method == 'POST':
        form = DnsClientForm(request.POST)
        if form.is_valid():
            if group.dnsclient_set.all():
                dnsclient = group.dnsclient_set.all()[0]
                dnsclient.domain = form.cleaned_data['domain']
                dnsclient.dns1_address = form.cleaned_data['dns1_address']
                dnsclient.dns2_address = form.cleaned_data['dns2_address']
                dnsclient.save()
            else:
                dnsclient = group.dnsclient_set.create(
                            domain = form.cleaned_data['domain'],
                            dns1_address = form.cleaned_data['dns1_address'],
                            dns2_address = form.cleaned_data['dns2_address']
                        )
            redis_json = dnsclient_redis_format(dnsclient)
            redis_key = "{}:{}:dnsclient_config".format(group.client_fk.client_name, group.group_name)
            Utils.redis_write(redis_key, redis_json)
    if group.dnsclient_set.all():
        dnsclient = group.dnsclient_set.all()[0]
        initial_values = {'domain': dnsclient.domain, 'dns1_address': dnsclient.dns1_address, 'dns2_address': dnsclient.dns2_address}
        form = DnsClientForm(initial=initial_values)
    else:
        form = DnsClientForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
    return render(request, 'dnsclient/dnsclient_edit.html',{
            'form': form,
        })
