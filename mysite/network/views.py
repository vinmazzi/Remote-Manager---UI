from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from group.models import Group
from .models import Network
from .forms import NetworkForm
from node.views import interface_redis_format
from mysite.utils import Utils
# Create your views here.

def network_list(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    group = Group.objects.get(pk=group_id)
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        bridge = request.POST.get('bridge')
        interface = request.POST.get('network_interface')
        bridge = ( False if bridge == None else True )
        if form.is_valid():
            new_network = group.network_set.create(
                    network_name = form.cleaned_data['network_name'],
                    network_interface = interface,
                    network_description = form.cleaned_data['network_description'],
                    network_bridge = bridge,
                    group_fk = group,
                    )
            new_network.save()
            return HttpResponseRedirect(reverse('network:list', kwargs={'group_id':group_id}))
    form = NetworkForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'network_description'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
            form.fields[field].widget.__dict__['attrs'].update({'style': 'height: 48px'})
    networks = group.network_set.all()
    av_interfaces = ['eth0', 'eth1', 'eth2', 'eth3', 'eth4', 'eth5', 'eth6']
    for network in networks:
        if network.network_interface in av_interfaces:
            av_interfaces.remove(network.network_interface)
    return render(request, 'network/group_network_list.html',{
            'group': group,
            'form': form,
            'interfaces': av_interfaces,
            'networks': networks
            })

def network_edit(request, network_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    network = Network.objects.get(pk=network_id)
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            for key in form.cleaned_data.keys():
                if form.cleaned_data[key] != None:
                   exec_string = "network.{} = \'{}\'".format(key, form.cleaned_data[key])
                   exec(exec_string)
            network.save()

            return HttpResponseRedirect(reverse('network:list', kwargs={'group_id': network.group_fk.pk}))
    else:
      initial_values = {'network_name': network.network_name, 'network_interface': network.network_interface, 'network_description': network.network_description}
      form = NetworkForm(initial=initial_values)
      return render(request, 'network/network_edit.html', {
          'network_id': network_id,
          'form': form,
          })

def network_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    network = Network.objects.get(pk=request.POST.get('network_id'))
    group_id = network.group_fk.pk
    network.delete()
    group = Group.objects.get(pk=group_id)
    for node in group.node_set.all():
        interfaces_json = interface_redis_format(node.interface_set.all())
        interfaces_key  = "Renner:{}:network_interfaces".format(node.name)
        Utils.redis_write(interfaces_key, interfaces_json)

    
    Utils.run_puppet(group.group_name)
    return HttpResponseRedirect(reverse('network:list', kwargs={'group_id': group_id}))
