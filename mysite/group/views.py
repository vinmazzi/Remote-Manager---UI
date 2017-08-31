from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from client.models import Client
from client.forms import ClientForm
from .models import Group
from .forms import GroupForm

# Create your views here.

def teste(request):
    return render(request, 'group/header.html')

def group(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    return render(request, 'group/client_groups.html', {
            'client_id': client_id,
        })

def group_create(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
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
        for field in form.fields:
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
            if (field == 'group_description'):
                form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
                form.fields[field].widget.__dict__['attrs'].update({'style': 'height: 48px'})
    return render(request, 'group/client_groups_create.html', {
                'client_id': client_id,
                'form': form,
            })

def group_list_config(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
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
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    try:
        group = Group.objects.get(pk=group_id)
    except (KeyError, Group.DoesNotExist):
        return render(request, 'group/client_groups_list_configure.html', {
                'error_massage': "No Clients yet!",
            })

    return render(request, 'group/client_groups_configure.html', {
            'group': group,
        })
