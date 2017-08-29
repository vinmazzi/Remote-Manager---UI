from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from client.models import Client
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
           if not value: pop_keys.append(key)

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
    else:
        for node in nodes:
            client_name.node_set.create(name=node['certname'].split('.')[0])
    return HttpResponseRedirect(reverse('node:list', kwargs={
            'client_id': client_id,
        }))
    
def node_list(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client = Client.objects.get(pk=client_id)
    nodes = client.node_set.all()
    return render(request, 'node/node_list.html', {
            'nodes': nodes,
            'client_id': client_id,
        })

def node_edit(request, node_id):
    node = Node.objects.get(pk=node_id)
    if request.method == 'POST':
        nodeForm = NodeForm(request.POST)
        interfaceForm = InterfaceForm(request.POST)
        network_hash = {}
        for network in node.group_fk.network_set.all():
            method_value = request.POST.get("{}_method".format(network))
            ip_value = request.POST.get("{}_ip".format(network))
            netmask_value = request.POST.get("{}_netmask".format(network))
            gateway_value = request.POST.get("{}_gateway".format(network))
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
            group_id = request.POST.get('group')
            group = node.client_fk.group_set.get(pk=group_id)
            node.group_fk = group
            key_name = "{}:{}:group".format(node.client_fk.client_name,node.name)
            key_value = group.group_name
            Utils.redis_write(key_name, key_value)
            for key in nodeForm.cleaned_data.keys():
                if nodeForm.cleaned_data[key] != None:
                   exec_string = "node.{} = \'{}\'".format(key, nodeForm.cleaned_data[key])
                   exec(exec_string)
                   if node.brand_new:
                       node.brand_new = False
            node.save()
            return HttpResponseRedirect(reverse('node:list', kwargs={'client_id': node.client_fk.pk}))
        else:
            return HttpResponse(form)
    nodeForm = NodeForm()
    interfaceForm = InterfaceForm()
    for field in nodeForm.fields:
        value_text = eval("node.%s" %(field))
        value_hash = {'value': value_text}
        nodeForm.fields[field].widget.__dict__['attrs'].update(value_hash)
        if field == "serial_number":
            nodeForm.fields[field].widget.__dict__['attrs'].update({'readonly': True})

    return render(request, 'node/node_edit.html', {
            'node_id': node_id,
            'node': node,
            'groups': node.client_fk.group_set.all(),
            'form': nodeForm,
            'interfaceForm': interfaceForm,
        })
