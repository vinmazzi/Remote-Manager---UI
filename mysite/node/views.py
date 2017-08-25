from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from client.models import Client
import urllib.request, urllib, json

# Create your views here.

def discovery_node(request, client_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_name = Client.objects.get(pk=client_id)
    query = '["and",["=","name","client_name"],["=","value","{}"]]\n'.format(client_name)
    url_values = urllib.parse.urlencode({'query': query})
    url = 'http://192.168.122.132:8080/pdb/query/v4/facts'
    full_url = url + "?" + url_values
    nodes = json.loads(str(urllib.request.urlopen(full_url).read(),'utf-8'))
    if client_name.node_set.all():
        for node in nodes:
            if not client_name.node_set.filter(name=node['certname'].split('.')[0]):
                client_name.node_set.create(name=node['certname'].split('.')[0])
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
