from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from client.models import Client
from client.forms import ClientForm
from .models import Group
from .forms import GroupForm

# Create your views here.

def group(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponse("Sem autenticar não entra.")
    return render(request, 'group/client_groups.html', {
            'client_id': client_id,
        })

def group_create(request, client_id):
    client = Client.objects.get(pk=client_id)

    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            client.group_set.create(
                    group_name  = form.cleaned_data['group_name_text'],
                    group_alias = form.cleaned_data['group_alias_text'],
                    group_description = form.cleaned_data['group_description'],
                    )

            return HttpResponseRedirect(reverse('group:index', kwargs={'client_id':client_id}))
    else:
        form = GroupForm()


    return render(request, 'group/client_groups_create.html', {
                'client_id': client_id,
                'form': form,
            })

def group_list_config(request, client_id):
    client = Client.objects.get(pk=client_id)
    try:
        groups = client.group_set.all()
    except (KeyError, Group.DoesNotExist):
        return render(request, 'group/client_groups_list_configure.html', {
                'error_massage': "No Clients yet!",
            })

    return render(request, 'group/client_groups_list_configure.html', {
            'groups': groups,
        })

def group_config(request, group_id):
    try:
        group = Group.objects.get(pk=group_id)
    except (KeyError, Group.DoesNotExist):
        return render(request, 'group/client_groups_list_configure.html', {
                'error_massage': "No Clients yet!",
            })

    return render(request, 'group/client_groups_configure.html', {
            'group': group,
        })
