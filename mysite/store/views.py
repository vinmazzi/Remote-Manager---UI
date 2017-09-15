from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.forms.models import model_to_dict
from .forms import StoreForm
from .models import Store
from client.models import Client
from group.models import Group

# Create your views here.

def store_create(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client = Client.objects.get(pk=client_id)
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            group_id = request.POST.get('group')
            group = Group.objects.get(pk=group_id)
            client.store_set.create(
                    name  = form.cleaned_data['name'],
                    code  = form.cleaned_data['code'],
                    country = form.cleaned_data['country'],
                    state = form.cleaned_data['state'],
                    city = form.cleaned_data['city'],
                    address = form.cleaned_data['address'],
                    group_fk = group,
                    )

            return HttpResponseRedirect(reverse('store:create', kwargs={'client_id':client_id}))
    else:
      form = StoreForm()
      for field in form.fields:
          form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
    return render(request, 'store/store_create.html', {
        'client_id': client_id, 
        'form':form,
        'groups': client.group_set.all()
        })

def store_list(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client = Client.objects.get(pk=client_id)
    stores = client.store_set.all()
    return render(request, 'store/store_list.html', {
            'stores': stores,
            'client_id': client_id
        })

def store_edit(request, store_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    store = Store.objects.get(pk=store_id) 
    if request.method == "POST":
        form = StoreForm(request.POST)
        if form.is_valid():
          group_id = request.POST.get('group')
          group = Group.objects.get(pk=group_id)
          store.group_fk = group
          for key in form.cleaned_data.keys():
              if form.cleaned_data[key] != None:
                  exec_string = "store.{} = \'{}\'".format(key, form.cleaned_data[key])
                  exec(exec_string)
        store.save()
        return HttpResponseRedirect(reverse('store:edit', kwargs={'store_id': store_id}))
    initial_values = {'name': store.name, 'code': store.code, 'country': store.country, 'state': store.state, 'city': store.city, 'address': store.address}
    form = StoreForm(initial=initial_values)
    for field in form.fields:
        if field == "code":
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
            form.fields[field].widget.__dict__['attrs'].update({'readonly': True})
        else:
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
    return render(request, 'store/store_edit.html', {
        'groups': store.client_fk.group_set.all(),
        'store':store,
        'form': form,
        })

def store_edit_menu(request, store_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    store = Store.objects.get(pk=store_id) 
    return render(request, 'store/store_edit_menu.html', {
        'store':store,
        })

def store_boxes(request, store_id):
    store = Store.objects.get(pk=store_id) 
    nodes = store.node_set.all()
    return render(request, 'store/store_boxes.html', {
        'store': store,
        'nodes': nodes,
        })
