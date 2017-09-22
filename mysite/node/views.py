from django.shortcuts import render
from django.contrib.auth.models import User, Group
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from client.models import Client
from store.models import Store
from .models import Node
from .forms import NodeForm
from network.forms import InterfaceForm
from django.forms.models import model_to_dict
import urllib.request, urllib, json, ast
from mysite.utils import Utils

# Create your views here.

def interface_redis_format(interfaces):
   interfaces_hash = {}
   for i in interfaces:
       dict_i = model_to_dict(i)
       pop_keys = ['node_fk', 'network_fk', 'id', 'gateway']
       tmp_interface_name = i.network_fk.network_interface

       for key,value in dict_i.items():
           if (not value) and (key not in pop_keys):
               pop_keys.append(key)

       for key in pop_keys:
           dict_i.pop(key)
   
       tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_interface_name, dict_i))
       interfaces_hash.update(tmp_format)

   return json.dumps(interfaces_hash)

def puppetdb_query(query):
    url_values = urllib.parse.urlencode({'query': query})
    url = 'http://192.168.122.132:8080/pdb/query/v4/facts'
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
                        dns1_ip = form.cleaned_data['dns1_ip'],
                        dns2_ip = form.cleaned_data['dns2_ip'],
                        dns_domain = form.cleaned_data['dns_domain'],
                        dns_search = form.cleaned_data['dns_domain'],
                    )
            key_name = "{}:{}:group".format(node.client_fk.client_name,node.name)
            key_value = store.group_fk.group_name
            Utils.redis_write(key_name, key_value)
            for network in node.group_fk.network_set.all():
                method_value = request.POST.get("{}_method".format(network.network_name))
                ip_value = request.POST.get("{}_ip".format(network.network_name))
                netmask_value = request.POST.get("{}_netmask".format(network.network_name))
                gateway_value = request.POST.get("{}_gateway".format(network.network_name))
                if network.network_interface not in str(node.interface_set.all()):
                    node.interface_set.create(
                            method = method_value,
                            ipaddress = ip_value,
                            netmask = netmask_value,
                            gateway = gateway_value,
                            network_fk = network, 
                            )
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
            interfaces_json = interface_redis_format(node.interface_set.all())
            interfaces_key = "{}:{}:network_interfaces".format(node.client_fk.client_name, node.name)
            Utils.redis_write(interfaces_key, interfaces_json)

            razor_tag_data = json.dumps({'name':node.name, 'rule': ["=",["fact","serialnumber"],node.serial_number]})
            razor_policy_data = json.dumps({"name": node.name, "repo": "centos7", "task": "centos", "broker": "puppet", "enabled": True,
                    "hostname": "{}.{}".format(node.name, node.dns_search),"root_password": "secret", "max_count": 20, "tags": [node.name] }) 
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
            if network.network_interface not in str(node.interface_set.all()):
                node.interface_set.create(
                        method = method_value,
                        ipaddress = ip_value,
                        netmask = netmask_value,
                        gateway = gateway_value,
                        network_fk = network, 
                        )
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

        interfaces_json = interface_redis_format(node.interface_set.all())
        interfaces_key = "Renner:{}:network_interfaces".format(node.name)
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
            return HttpResponseRedirect(reverse('node:list', kwargs={'client_id': client_id}))
        else:
            return HttpResponse(form)
    nodeForm = NodeForm()
    interfaceForm = InterfaceForm()
    interface_set = []
    for i in node.interface_set.all():
        interface_set.append(i.network_fk.network_interface)
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
            'client_id': client_id
        })
