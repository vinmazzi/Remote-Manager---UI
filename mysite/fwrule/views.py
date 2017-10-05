from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.conf import settings
from django import forms
from django.forms.models import model_to_dict
from .models import Firewall_rule
from .forms import FwRuleForm
from network.models import Network
from client.models import Client
from client.forms import ClientForm
from group.models import Group
from group.forms import GroupForm
import redis, ast, json, paramiko

def run_puppet(group_name):
   ssh = paramiko.SSHClient()
   try:
       ssh.load_system_host_keys()
       ssh.connect('192.168.1.201', username="mcollective", password="mcollective")
       stdin, stdout,stder = ssh.exec_command("/opt/puppetlabs/bin/mco puppet runonce -F group_name={}".format(group_name))
       ssh.close
   except Exception as err:
       return HttpResponse(err)

def fwrules_redis_format(fwrules):
   fwrules_hash = {}
   for f in fwrules:
       group = f.group_fk
       networks = group.network_set.all()
       dict_f = model_to_dict(f)
       pop_keys = ['rule_name_text', 'group_fk', 'id']

       if Network.objects.filter(network_name=f.source.split("-")[0]):
           network = Network.objects.filter(network_name=f.source.split("-")[0])[0]
           if "network" in f.source:
               dict_f['source'] = "%%{facts.networking.interfaces.%s.network}" %(network.network_interface)
           elif "gateway" in f.source:
               dict_f['source'] = "%%{facts.networking.interfaces.%s.ip}" %(network.network_interface)

       if Network.objects.filter(network_name=f.destination.split("-")[0]):
           network = Network.objects.filter(network_name=f.destination.split("-")[0])[0]
           if "network" in f.destination:
               dict_f['destination'] = "%%{facts.networking.interfaces.%s.network}" %(network.network_interface)
           elif "gateway" in f.destination:
               dict_f['destination'] = "%%{facts.networking.interfaces.%s.ip}" %(network.network_interface)

       for key,value in dict_f.items():
           if not value: pop_keys.append(key)
           if key == "source" and value == "all": pop_keys.append(key)
           if key == "destination" and value == "all": pop_keys.append(key)

       if not dict_f['action'] in {'accept', 'drop', 'reject'}:
           tmp_value = dict_f['action'].upper()
           dict_f.pop('action')
           jump_dict = {'jump': tmp_value}
           dict_f.update(jump_dict)
   
       for key in pop_keys:
           dict_f.pop(key)
   
       tmp_rule_name = f.rule_name_text
       tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_rule_name, dict_f))
       fwrules_hash.update(tmp_format)

   return json.dumps(fwrules_hash)

def redis_write(key_name, value):
   host_ip = "192.168.1.201"
   tcp_port = 6379
   try:
       rc = redis.StrictRedis(host=host_ip, port=tcp_port, db=0)
       rc.set(key_name, value)
   except Exception as err:
       return HttpResponse(err)

def fwrules(request, group_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    group = client.group_set.get(pk=group_id)
    networks = group.network_set.all()

    if request.method == 'POST':
        form = FwRuleForm(request.POST)
        source_ip = request.POST.get('source')
        destination_ip = request.POST.get('destination')
        protocol = request.POST.get('protocol')
        table = request.POST.get('table')
        chain = request.POST.get('chain')
        custom_source = request.POST.get('source-custom')
        custom_destination = request.POST.get('destination-custom')
        action = request.POST.get('action')

        if form.is_valid():
            if custom_source and custom_destination:
                source = custom_source
                destination = custom_destination
            elif custom_source:
                source = custom_source
                destination = destination_ip
            elif custom_destination:
                source = source_ip
                destination = custom_destination
            else:
                source = source_ip
                destination = destination_ip

            new_fwrule = group.firewall_rule_set.create(  
                    rule_name_text   = form.cleaned_data['rule_name_text'],
                    source           = source,
                    destination      = destination,
                    proto            = protocol,
                    action           = action,
                    chain            = chain.upper(),
                    table            = table,
                    sport            = form.cleaned_data['sport'], 
                    dport            = form.cleaned_data['dport'])

            fwrules  = group.firewall_rule_set.all()
            key_name = "{}:{}:fwrules".format(client.client_name, group.group_name)
            json_fwrule = fwrules_redis_format(fwrules)
            redis_write(key_name, json_fwrule)
            run_puppet(group.group_name)

            return HttpResponseRedirect(reverse('fwrule:fwrules', kwargs={'group_id':group_id}))
    else:
        form = FwRuleForm()
        for field in form.fields:
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})

    try:
        fwrules = group.firewall_rule_set.all()
    except (KeyError, Firewall_rule.DoesNotExist):
        return render(request, 'fwrule/group_fwrule_create.html', {
            'error_message': "No Firewall rules yet.",
            'form': form,
            'group_id': group_id,
            'client_id': client_id,
        })

    return render(request, 'fwrule/group_fwrule_list.html', {
               'form': form,
               'fwrules': fwrules,
               'group': group,
               'group_id': group_id,
               'networks': networks,
            })

def fwrules_edit(request, fwrule_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))

    fwrule = Firewall_rule.objects.get(pk=fwrule_id)
    group_name = fwrule.group_fk.group_name
    client_name = fwrule.group_fk.client_fk.client_name

    if request.method == 'POST':
        if request.user.has_perm('fwrule.change_firewall_rule'):
           form = FwRuleForm(request.POST)
           if form.is_valid():
               for key in form.cleaned_data.keys():
                   if form.cleaned_data[key] != None:
                      exec_string = "fwrule.{} = \'{}\'".format(key, form.cleaned_data[key])
                      exec(exec_string)
               fwrule.save()
               key_name = "{}:{}:fwrules".format(client_name, group_name)
               json_fwrule = fwrules_redis_format(fwrule.group_fk.firewall_rule_set.all())
               redis_write(key_name, json_fwrule)
               run_puppet(group_name)

               return HttpResponseRedirect(reverse('fwrule:fwrules', kwargs={'group_id': fwrule.group_fk.pk}))
    else:
       form = FwRuleForm()
       for field in form.fields:
           value_text = eval("fwrule.%s" %(field))
           value_hash = {'value': value_text}
           form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
           form.fields[field].widget.__dict__['attrs'].update(value_hash) 

       return render(request, 'fwrule/fwrules_edit.html', {
           'fwrule_id': fwrule_id,
           'fwrule': fwrule,
           'networks': fwrule.group_fk.network_set.all(),
           'form': form,
           })

def fwrules_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))

    fwrule = Firewall_rule.objects.get(pk=request.POST.get('firewall_id'))
    if request.user.has_perm('fwrule.delete_firewall_rule'):
       group_name = fwrule.group_fk.group_name
       client_name = fwrule.group_fk.client_fk.client_name
       fwrule.delete()

       key_name = "{}:{}:fwrules".format(client_name, group_name)
       json_fwrule = fwrules_redis_format(fwrule.group_fk.firewall_rule_set.all())
       redis_write(key_name, json_fwrule)
       run_puppet(group_name)

    return HttpResponseRedirect(reverse('fwrule:fwrules', kwargs={'group_id': fwrule.group_fk.pk}))
    

