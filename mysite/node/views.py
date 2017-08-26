from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from client.models import Client
from .models import Node
from .forms import NodeForm
import urllib.request, urllib, json

# Create your views here.

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
        form = NodeForm(request.POST)
        if form.is_valid():
            group_id = request.POST.get('group')
            group = node.client_fk.group_set.get(pk=group_id)
            node.group_fk = group
            for key in form.cleaned_data.keys():
                if form.cleaned_data[key] != None:
                   exec_string = "node.{} = \'{}\'".format(key, form.cleaned_data[key])
                   exec(exec_string)
                   if node.brand_new:
                       node.brand_new = False
            node.save()
            return HttpResponseRedirect(reverse('node:list', kwargs={'client_id': node.client_fk.pk}))
        else:
            return HttpResponse(form)
    form = NodeForm()
    for field in form.fields:
        value_text = eval("node.%s" %(field))
        value_hash = {'value': value_text}
        form.fields[field].widget.__dict__['attrs'].update(value_hash)
        if field == "serial_number":
            form.fields[field].widget.__dict__['attrs'].update({'readonly': True})

    return render(request, 'node/node_edit.html', {
            'node_id': node_id,
            'node': node,
            'groups': node.client_fk.group_set.all(),
            'form': form,
        })
