from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from group.models import Group
from mysite.utils import Utils
from django.forms.models import model_to_dict
import urllib.request, urllib, json, ast
from .models import Registry
from .forms import RegistryForm

def options(request, group_id):
    group = Group.objects.get(pk=group_id)
    return render(request, 'micro_service/micro_service_options.html', {
                    'group': group,
                    })

def registry_redis_format(registries):
    registry_hash = {}
    for registry in registries:
        dict_reg = model_to_dict(registry)
        pop_keys = ['id', 'name', 'port', 'group_fk','description', 'url']
        tmp_registry_name = "{}:{}".format(registry.url,registry.port)

        for key,value in dict_reg.items():
            if (not value) and (key not in pop_keys):
                pop_keys.append(key)

        for key in pop_keys:
            dict_reg.pop(key)

        tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_registry_name, dict_reg))
        registry_hash.update(tmp_format)

    return json.dumps(registry_hash)

def registry_edit(request, registry_id):
    registry = Registry.objects.get(pk=registry_id)
    if request.method == "POST":
        registry.name = request.POST.get('modal_name')
        registry.url = request.POST.get('modal_url')
        registry.port = request.POST.get('modal_port')
        registry.user = request.POST.get('modal_user')
        registry.port = request.POST.get('modal_port')
        registry.password = request.POST.get('modal_password')
        registry.email = request.POST.get('modal_email')
        registry.ca_crt = request.POST.get('modal_ca_crt')
        registry.description = request.POST.get('modal_description')
        registry.save()
        group = registry.group_fk
        registries = group.registry_set.all()
        registry_json_hash = registry_redis_format(group.registry_set.all())
        registry_redis_key = "{}:{}:registries".format(group.client_fk.client_name, group.group_name)
        Utils.redis_write(registry_redis_key, registry_json_hash)
        return HttpResponseRedirect(reverse('micro_service:registry_list', kwargs={'group_id':group.pk}))

    return HttpResponse(json.dumps(model_to_dict(registry)), content_type="application/json")

def registry_delete(request):
    registry = Registry.objects.get(pk=request.POST.get('registry_id'))
    group = registry.group_fk
    registries = group.registry_set.all()
    registry.delete()
    registry_json_hash = registry_redis_format(group.registry_set.all())
    registry_redis_key = "{}:{}:registries".format(group.client_fk.client_name, group.group_name)
    Utils.redis_write(registry_redis_key, registry_json_hash)

    return HttpResponseRedirect(reverse('micro_service:registry_list', kwargs={'group_id':group.pk}))


def registry_list(request, group_id):
    group = Group.objects.get(pk=group_id)
    registries = group.registry_set.all()
    if request.method == 'POST':
        form = RegistryForm(request.POST)
        if form.is_valid():
            group.registry_set.create(
                       name = form.cleaned_data['name'],
                       description = form.cleaned_data['description'],
                       url = form.cleaned_data['url'],
                       port = form.cleaned_data['port'],
                       user = form.cleaned_data['user'],
                       password = form.cleaned_data['password'],
                       ca_crt = form.cleaned_data['ca_crt'],
                       email = form.cleaned_data['email'],
                    )

            registry_json_hash = registry_redis_format(group.registry_set.all())
            registry_redis_key = "{}:{}:registries".format(group.client_fk.client_name, group.group_name)
            Utils.redis_write(registry_redis_key, registry_json_hash)

            return HttpResponseRedirect(reverse('micro_service:registry_list', kwargs={'group_id':group_id}))
    form = RegistryForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description' or field == 'ca_crt'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
            if (field == 'ca_crt' ):
                form.fields[field].widget.__dict__['attrs'].update({'style': 'height: 50px; width: 545px'})
            else:
                form.fields[field].widget.__dict__['attrs'].update({'style': 'height: 50px'})

    return render(request, 'micro_service/registry_list.html',{
            'group': group,
            'registries': registries,
            'form': form,
        })
