from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from group.models import Group
from mysite.utils import Utils
from django.forms.models import model_to_dict
import urllib.request, urllib, json, ast
from .models import Registry, Container_catalog, Container
from network.models import Network
from .forms import RegistryForm, ContainerCatalogForm

def options(request, group_id):
    group = Group.objects.get(pk=group_id)
    return render(request, 'micro_service/micro_service_options.html', {
                    'group': group,
                    })

def container_redis_format(containers):
    host_containers = {}
    if containers:
        for container in containers:
            node = container.node_fk
            if node not in host_containers.keys():
                host_containers[node] = {'redis_key': "{}:{}:containers".format(node.client_fk.client_name, node.name)}
            network_name = container.container_catalog_fk.network_fk.network_name
            network_ip = container.ipaddress
            image_name = container.container_catalog_fk.image_name
            container_name = container.container_catalog_fk.name.replace(" ", "_")
            registry = "{}:{}".format(container.container_catalog_fk.registry_fk.url, container.container_catalog_fk.registry_fk.port)
            container_hash_tmp = {container_name: {'primitive_class': 'ocf',
                    'provided_by': 'heartbeat',
                    'primitive_type': 'docker', 
                    'parameters': {
                         'image': "%s/%s:latest" %(registry,image_name),
                         'name': container_name,
                         'run_opts': "--network %s --ip %s" %(network_name, network_ip),
                        }}}
            host_containers[node].update(container_hash_tmp)
    for key in host_containers.keys():
        redis_key = host_containers[key]['redis_key']
        host_containers[key].pop('redis_key')
        redis_value = json.dumps(host_containers[key])
        Utils.redis_write(redis_key, redis_value)

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

def catalog_list(request, group_id):
    group = Group.objects.get(pk=group_id)
    catalog = group.container_catalog_set.all()
    registries = group.registry_set.all()
    networks = group.network_set.filter(network_bridge=True)
    host_octect_list = list(range(2,255))
    for container in catalog:
        if container.host_octect in host_octect_list: host_octect_list.remove(container.host_octect)
    if request.method == 'POST':
        form = ContainerCatalogForm(request.POST)
        if form.is_valid():
            container_catalog = group.container_catalog_set.create(
                       name = form.cleaned_data['name'], 
                       description = form.cleaned_data['description'], 
                       image_name = form.cleaned_data['image_name'], 
                       network_fk = group.network_set.get(pk=request.POST.get('network')),
                       registry_fk = group.registry_set.get(pk=request.POST.get('registry')), 
                       host_octect = request.POST.get('host_octect'),
                    )
            for node in group.node_set.all():
                if node.interface_set.filter(network_fk=container_catalog.network_fk):
                    host_ipaddress = node.interface_set.filter(network_fk=container_catalog.network_fk)[0].ipaddress
                    network_tmp = host_ipaddress.split(".")
                    container_ip = "{}.{}.{}.{}".format(network_tmp[0], network_tmp[1], network_tmp[2],container_catalog.host_octect)
                    node.container_set.create(
                                container_catalog_fk = container_catalog,
                                ipaddress = container_ip,
                            )
            container_redis_format(Container.objects.all())
            return HttpResponseRedirect(reverse('micro_service:catalog_list', kwargs={'group_id':group.pk}))
    form = ContainerCatalogForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description' or field == 'ca_crt'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
            form.fields[field].widget.__dict__['attrs'].update({'style': 'height: 50px'})
    return render(request, 'micro_service/service_catalog_list.html', {
            'form': form,
            'registries': registries,
            'networks': networks,
            'catalog': catalog,
            'host_octect_list': host_octect_list,
        })

def container_edit(request, container_id):
    container = Container_catalog.objects.get(pk=container_id)
    if request.method == "POST":
        container.name = request.POST.get('modal_container_name')
        container.description = request.POST.get('modal_container_description')
        container.image_name = request.POST.get('modal_container_image_name')
        container.network_fk = Network.objects.get(pk=request.POST.get('modal_network'))
        container.registry_fk = Registry.objects.get(pk=request.POST.get('modal_registry'))
        container.save()
        return HttpResponseRedirect(reverse('micro_service:catalog_list', kwargs={'group_id':container.group_fk.pk}))

    return HttpResponse(json.dumps(model_to_dict(container)), content_type="application/json")

def catalog_container_delete(request):
    container = Container_catalog.objects.get(pk=request.POST.get('container_id'))
    group = container.group_fk
    container.delete()
    container_redis_format(Container.objects.all())

    return HttpResponseRedirect(reverse('micro_service:catalog_list', kwargs={'group_id':group.pk}))
