from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from client.models import Client
from store.models import Store
from .models import Node
from .forms import NodeForm
from route.models import Route
from network.forms import InterfaceForm
from django.forms.models import model_to_dict
import urllib.request, urllib, json, ast
from mysite.utils import Utils
from micro_service.models import Container

# Create your views here.

def redis_route_format(routes):
    routes_hash = {}
    for route in routes:
        dict_r = model_to_dict(route)
        pop_keys = ['id', 'interface_fk']
        iface = route.interface_fk
        if iface.bridge:
            tmp_interface_name = iface.network_fk.network_interface
            iface_name = "br%s" %(list(filter(str.isdigit,tmp_interface_name))[0])
        else:
            iface_name = iface.network_fk.network_interface

        dict_r.update({'interface': iface_name})
        if route.network == 'default':
            route_name = route.network

        for key in pop_keys:
            dict_r.pop(key)
        
        tmp_format = ast.literal_eval("{\'%s\': %s}" %(route_name, dict_r))
        routes_hash.update(tmp_format)

    return json.dumps(routes_hash)

def interface_redis_format(interfaces):
   interfaces_hash = {}
   for i in interfaces:
       dict_i = model_to_dict(i)
       pop_keys = ['bridge','node_fk', 'network_fk', 'id', 'gateway']
       tmp_interface_name = i.network_fk.network_interface

       if i.node_fk.group_fk.dnsclient_set.all():
           iface_options = {'options': {'PEERDNS': 'no'}}
           dict_i.update(iface_options)

       for key,value in dict_i.items():
           if (not value) and (key not in pop_keys):
               pop_keys.append(key)

       for key in pop_keys:
           dict_i.pop(key)

       tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_interface_name, dict_i))

       if i.bridge:
           for key in ['ipaddress', 'netmask']: 
               tmp_format[tmp_interface_name].pop(key)
           bridge_name = "br%s" %(list(filter(str.isdigit,tmp_interface_name))[0])
           if 'options' in tmp_format[tmp_interface_name]:
               tmp_format[tmp_interface_name]['options'].update({'BRIDGE': bridge_name})
           else:
               tmp_format[tmp_interface_name].update({'options': {'BRIDGE': bridge_name}})
           bridge_hash = {bridge_name: {'method': 'static', 'options': {'TYPE': 'Bridge'}, 'ipaddress': i.ipaddress,'netmask': i.netmask}}
           tmp_format.update(bridge_hash)
       interfaces_hash.update(tmp_format)

   return json.dumps(interfaces_hash)

def docker_network_redis_format(interfaces):
    docker_network_hash = {}
    for interface in interfaces:
        if interface.bridge:
            ip_blocks = interface.ipaddress.split('.')
            netmask = interface.netmask
            cidr = sum([bin(int(x)).count("1") for x in netmask.split(".")])
            network = "{}.{}.{}.0/{}".format(ip_blocks[0],ip_blocks[1], ip_blocks[2], cidr)
            gateway = interface.ipaddress
            network_range = "{}.{}.{}.50/31".format(ip_blocks[0],ip_blocks[1], ip_blocks[2])
            network_name = interface.network_fk.network_name
            network_type = "bridge"
            bridge_name = "br%s" %(list(filter(str.isdigit,interface.network_fk.network_interface))[0])
            options = "com.docker.network.bridge.name={}".format(bridge_name)
            tmp_hash = {network_name: {'driver': network_type, 'subnet': network, 'gateway': gateway, 'ip_range': network_range, 'options': options}}
            docker_network_hash.update(tmp_hash)
    return json.dumps(docker_network_hash)
    
def puppetdb_query(query):
    url_values = urllib.parse.urlencode({'query': query})
    url = 'http://192.168.1.201:8080/pdb/query/v4/facts'
    full_url = url + "?" + url_values
    result = json.loads(str(urllib.request.urlopen(full_url).read(),'utf-8'))
    return result

def discovery_node(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_name = Client.objects.get(pk=client_id)
    puppet_nodes_query = '["and",["=","name","client_name"],["=","value","{}"]]\n'.format(client_name)
    nodes = puppetdb_query(puppet_nodes_query)
    if client_name.node_set.all():
        for node in nodes:
            if not client_name.node_set.filter(name=node['certname'].split('.')[0]):
                serial_number_query = '["and",["=","name","serial_number"],["~","certname", "{}."]]\n'.format(node['certname'].split('.')[0])
                serial_number_result = puppetdb_query(serial_number_query)[0]['value']
                client_name.node_set.create(name=node['certname'].split('.')[0], brand_new=True, serial_number=serial_number_result)
                Utils.create_certificate(node['certname'].split('.')[0])
    else:
        for node in nodes:
            client_name.node_set.create(name=node['certname'].split('.')[0])
            Utils.create_certificate(node['certname'])
    return HttpResponseRedirect(reverse('node:list', kwargs={
            'client_id': client_id,
        }))
    
def node_create(request, store_id):
    try:
        store = Store.objects.get(pk=store_id)
    except:
        return HttpResponse(store_id)
    client = store.client_fk
    if request.method == "POST":
        form = NodeForm(request.POST)
        if form.is_valid():
            node = Node.objects.create(
                        name = form.cleaned_data['name'],
                        serial_number = form.cleaned_data['serial_number'],
                        client_fk = store.client_fk,
                        group_fk = store.group_fk,
                        store_fk = store,
                    )
            key_name = "{}:{}:group".format(node.client_fk.client_name,node.name)
            key_value = store.group_fk.group_name
            Utils.redis_write(key_name, key_value)
            for network in node.group_fk.network_set.all():
                method_value = ("static" if network.network_bridge else request.POST.get("{}_method".format(network.network_name)))
                ip_value = request.POST.get("{}_ip".format(network.network_name))
                netmask_value = request.POST.get("{}_netmask".format(network.network_name))
                gateway_value = request.POST.get("{}_gateway".format(network.network_name))
                bridge = network.network_bridge
                if network.network_interface not in str(node.interface_set.all()):
                    iface = node.interface_set.create(
                              method = method_value,
                              ipaddress = ip_value,
                              bridge = bridge,
                              netmask = netmask_value,
                              gateway = gateway_value,
                              network_fk = network, 
                            )
                    if network.network_default_gateway:
                        iface.route_set.create(
                                   network = "default",
                                   gateway = gateway_value,
                                   netmask = netmask_value,
                                )
                        routes_value = redis_route_format(iface.route_set.all())
                        routes_key = "{}:{}:routes".format(node.client_fk.client_name, node.name)
                        Utils.redis_write(routes_key, routes_value)
                else:
                    iface = node.interface_set.get(network_fk=network)
                    iface.method = method_value
                    if(iface.method == "dhcp"):
                       iface.ipaddress = ""
                       iface.netmask = ""
                       iface.gateway = ""
                    else:
                       iface.ipaddress = ip_value
                       iface.netmask = netmask_value
                       iface.gateway = gateway_value
                       iface.bridge = bridge
                    iface.network_fk = network
                    iface.save()
            for container in node.group_fk.container_catalog_set.all():
                container_ip_address_field = "{}_ip_address".format(container.name.replace(" ", "_"))
                if request.POST.get(container_ip_address_field):
                    node.container_set.create(
                                container_catalog_fk = container,
                                ipaddress = request.POST.get(container_ip_address_field),
                            )
            Utils.single_container_redis_format(node.container_set.all())
            interfaces_json = interface_redis_format(node.interface_set.all())
            interfaces_key = "{}:{}:network_interfaces".format(node.client_fk.client_name, node.name)
            docker_network_json = docker_network_redis_format(node.interface_set.all())
            docker_network_key = "{}:{}:docker_networks".format(node.client_fk.client_name, node.name)
            Utils.redis_write(interfaces_key, interfaces_json)
            Utils.redis_write(docker_network_key, docker_network_json)

            dnsclient = node.group_fk.dnsclient_set.all()[0]
            #razor_tag_data = json.dumps({'name':node.name, 'rule': ["=",["fact","serialnumber"],node.serial_number]})
            razor_tag_data = json.dumps({'name':node.name, 'rule': ["=",["fact","boardserialnumber"],node.serial_number]})
            razor_policy_data = json.dumps({"name": node.name, "repo": "centos7", "task": "centos", "broker": "puppet", "enabled": True,
                    "hostname": "{}.{}".format(node.name, dnsclient.domain),"root_password": "secret", "max_count": 20, "tags": [node.name] }) 
            Utils.razor_write(razor_tag_data, 'create-tag')
            Utils.razor_write(razor_policy_data, 'create-policy')
            return HttpResponseRedirect(reverse('node:create', kwargs={'store_id': store_id}))
    if not store.node_set.all():
        node_name = "{}{}box0".format(client.client_alias,store.code)
    else:
        node_name = "{}{}box{}".format(client.client_alias, store.code, len(store.node_set.all()))
    form = NodeForm(initial={'name': node_name})
    for field in form.fields:
        if field == "name":
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
            form.fields[field].widget.__dict__['attrs'].update({'readonly': True})

        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
    return render(request, 'node/node_create.html', {
        'client_id': client.pk,
        'store': store,
        'group': store.group_fk,
        'form': form,
        'interface_set': [],
        })

def node_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    nodes = client.node_set.all()
    return render(request, 'node/node_list.html', {
            'nodes': nodes,
        })

def node_edit(request, node_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    user_object = User.objects.get(username=request.user.username)
    client_id = user_object.userextrainfo_set.all()[0].client_fk.pk
    node = Node.objects.get(pk=node_id)
    if request.method == 'POST':
        nodeForm = NodeForm(request.POST)
        interfaceForm = InterfaceForm(request.POST)
        network_hash = {}
        for network in node.group_fk.network_set.all():
            method_value = request.POST.get("{}_method".format(network.network_name))
            ip_value = request.POST.get("{}_ip".format(network.network_name))
            netmask_value = request.POST.get("{}_netmask".format(network.network_name))
            gateway_value = request.POST.get("{}_gateway".format(network.network_name))
            bridge = network.network_bridge
            if network.network_interface not in str(node.interface_set.all()):
                iface = node.interface_set.create(
                          method = method_value,
                          ipaddress = ip_value,
                          netmask = netmask_value,
                          gateway = gateway_value,
                          network_fk = network, 
                          bridge = bridge,
                        )
                if iface.network_fk.network_default_gateway:
                    iface.route_set.create(
                               network = "default",
                               gateway = gateway_value,
                               netmask = netmask_value,
                            )
                    routes_value = redis_route_format(iface.route_set.all())
                    routes_key = "{}:{}:routes".format(node.client_fk.client_name, node.name)
                    Utils.redis_write(routes_key, routes_value)
            else:
                iface = node.interface_set.get(network_fk=network)
                iface.method = method_value
                if(iface.method == "dhcp"):
                   iface.ipaddress = ""
                   iface.netmask = ""
                   iface.gateway = ""
                else:
                   iface.ipaddress = ip_value
                   iface.netmask = netmask_value
                   iface.gateway = gateway_value
                iface.network_fk = network
                iface.save()
                if iface.network_fk.network_default_gateway:
                    if not iface.route_set.get(network='default'):
                       iface.route_set.create(
                                  network = "default",
                                  gateway = gateway_value,
                                  netmask = netmask_value,
                               )
                    routes_value = redis_route_format(iface.route_set.all())
                    routes_key = "{}:{}:routes".format(node.client_fk.client_name, node.name)
                    Utils.redis_write(routes_key, routes_value)
        for container in node.group_fk.container_catalog_set.all():
            container_ip_address_field = "{}_ip_address".format(container.name.replace(" ", "_"))
            if container.name not in str(node.container_set.all()):
                if request.POST.get(container_ip_address_field):
                    node.container_set.create(
                                container_catalog_fk = container,
                                ipaddress = request.POST.get(container_ip_address_field),
                            )
            else:
                node_container = node.container_set.get(container_catalog_fk=container)
                if(request.POST.get(container_ip_address_field) != node_container.ipaddress):
                    node_container.ipaddress = request.POST.get(container_ip_address_field)
                    node_container.save()
        Utils.single_container_redis_format(node.container_set.all())
        interfaces_json = interface_redis_format(node.interface_set.all())
        interfaces_key = "Renner:{}:network_interfaces".format(node.name)
        docker_network_json = docker_network_redis_format(node.interface_set.all())
        docker_network_key = "{}:{}:docker_networks".format(node.client_fk.client_name, node.name)
        Utils.redis_write(docker_network_key, docker_network_json)
        Utils.redis_write(interfaces_key, interfaces_json)
        Utils.run_puppet(node.group_fk.group_name)

        if nodeForm.is_valid():
            for key in nodeForm.cleaned_data.keys():
                if nodeForm.cleaned_data[key] != None:
                   exec_string = "node.{} = \'{}\'".format(key, nodeForm.cleaned_data[key])
                   exec(exec_string)
                   if node.brand_new:
                       node.brand_new = False
            node.save()
            return HttpResponseRedirect(reverse('node:list'))
        else:
            return HttpResponse(form)
    nodeForm = NodeForm()
    interfaceForm = InterfaceForm()
    interface_set = []
    container_set = []
    for i in node.interface_set.all():
        interface_set.append(i.network_fk.network_interface)
    for container in node.container_set.all():
        container_set.append(container.container_catalog_fk.name)
    for field in nodeForm.fields:
        if field == "store":
            store = node.store_fk.name
            store_code = node.store_fk.code
            value_text = "{} - {}".format(store,store_code)
            value_hash = {'value': value_text}
            nodeForm.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
            nodeForm.fields[field].widget.__dict__['attrs'].update(value_hash)
            nodeForm.fields[field].widget.__dict__['attrs'].update({'readonly': True})
        else:
            value_text = eval("node.%s" %(field))
            value_hash = {'value': value_text}
            nodeForm.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
            nodeForm.fields[field].widget.__dict__['attrs'].update(value_hash)
            if field == "serial_number" or field == "name":
                #nodeForm.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
                nodeForm.fields[field].widget.__dict__['attrs'].update({'readonly': True})

    return render(request, 'node/node_edit.html', {
            'node_id': node_id,
            'node': node,
            'form': nodeForm,
            'interfaceForm': interfaceForm,
            'interface_set': interface_set,
            'container_set': container_set,
            'client_id': client_id,
            'group': node.group_fk,
            'ip_teste': '33'
        })
