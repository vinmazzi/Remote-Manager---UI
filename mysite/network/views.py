from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from group.models import Group
from .models import Network
from .forms import NetworkForm
# Create your views here.

def network_list(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    group = Group.objects.get(pk=group_id)
    if request.method == 'POST':
        form = NetworkForm(request.POST)
        if form.is_valid():
            new_network = group.network_set.create(
                    network_name = form.cleaned_data['network_name'],
                    network_interface = form.cleaned_data['network_interface'],
                    network_description = form.cleaned_data['network_description'],
                    group_fk = group,
                    )
            new_network.save()
            return HttpResponseRedirect(reverse('network:list', kwargs={'group_id':group_id}))
    form = NetworkForm()
    networks = group.network_set.all()
    return render(request, 'network/group_network_list.html',{
            'group': group,
            'form': form,
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

    return HttpResponseRedirect(reverse('network:list', kwargs={'group_id': group_id}))
