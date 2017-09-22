from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from group.models import Group
from mysite.utils import Utils
from .models import Ntp
from .forms import NtpForm
import json

# Create your views here.

def ntp_redis_format(ntp):
    servers_array = ntp.servers.split(',')
    return json.dumps(servers_array)

def ntp_edit(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    group = Group.objects.get(pk=group_id)
    if request.method == 'POST':
        form = NtpForm(request.POST)
        if form.is_valid():
            if group.ntp_set.all():
                ntp = group.ntp_set.all()[0]
                ntp.servers = form.cleaned_data['servers']
                ntp.save()
                redis_json = ntp_redis_format(ntp)
            else:
                group.ntp_set.create(servers = form.cleaned_data)
                redis_json = ntp_redis_format(group.ntp_set.all()[0].servers)
            redis_key = "{}:{}:ntp_servers".format(group.client_fk.client_name, group.group_name)
            Utils.redis_write(redis_key, redis_json)
    if group.ntp_set.all():
        ntp = group.ntp_set.all()[0]
        initial_values = {'servers': ntp.servers}
        form = NtpForm(initial=initial_values)
    else:
        form = NtpForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control tagsinput'})
    return render(request,'ntp/ntp_edit.html', {
        'form': form,
        'group_name': group.group_name,
        })
