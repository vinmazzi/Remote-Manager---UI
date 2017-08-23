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
from client.models import Client
from client.forms import ClientForm
from group.models import Group
from group.forms import GroupForm
import redis, ast, json, paramiko

def teste(request):
    return render(request, 'mzbox/index.html')

def run_puppet(group_name):
   ssh = paramiko.SSHClient()
   try:
       ssh.load_system_host_keys()
       ssh.connect('192.168.122.132', username="mcollective", password="mcollective")
       stdin, stdout,stder = ssh.exec_command("/opt/puppetlabs/bin/mco puppet runonce -F group_name={}".format(group_name))
       ssh.close
   except Exception as err:
       return HttpResponse(err)

def fwrules_redis_format(fwrules):
   fwrules_hash = {}
   for f in fwrules:
       dict_f = model_to_dict(f)
       pop_keys = ['rule_name_text', 'group_fk', 'id']
       for key,value in dict_f.items():
           if not value: pop_keys.append(key)
   
       for key in pop_keys:
           dict_f.pop(key)
   
       tmp_rule_name = f.rule_name_text
       tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_rule_name, dict_f))
       fwrules_hash.update(tmp_format)

   return json.dumps(fwrules_hash)

def redis_write(key_name, value):
   host_ip = "192.168.122.132"
   tcp_port = 6379
   try:
       rc = redis.StrictRedis(host=host_ip, port=tcp_port, db=0)
       rc.set(key_name, value)
   except Exception as err:
       return HttpResponse(err)

def fwrules(request, client_id, group_id):
    client = Client.objects.get(pk=client_id)
    group = client.group_set.get(pk=group_id)

    if request.method == 'POST':
        form = FwRuleForm(request.POST)
        if form.is_valid():
          
           new_fwrule = group.firewall_rule_set.create(  
                   rule_name_text   = form.cleaned_data['rule_name_text'],
                   source           = form.cleaned_data['source'],
                   destination      = form.cleaned_data['destination'],
                   proto            = form.cleaned_data['proto'],
                   action           = form.cleaned_data['action'],
                   chain            = form.cleaned_data['chain'].upper(),
                   table            = form.cleaned_data['table'],
                   sport            = form.cleaned_data['sport'], 
                   dport            = form.cleaned_data['dport'])

           fwrules = group.firewall_rule_set.all()
           key_name = "{}:{}:fwrules".format(client.client_name, group.group_name)
           json_fwrule = fwrules_redis_format(fwrules)
           redis_write(key_name, json_fwrule)
           run_puppet(group.group_name)

           return HttpResponseRedirect(reverse('fwrule:fwrules', kwargs={'client_id':client_id, 'group_id':group_id}))
    else:
        form = FwRuleForm()

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
               'client_id': client_id,
            })

def fwrules_edit(request, fwrule_id):
    fwrule = Firewall_rule.objects.get(pk=fwrule_id)
    group_name = fwrule.group_fk.group_name
    client_name = fwrule.group_fk.client_fk.client_name

    if request.method == 'POST':
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

            return HttpResponseRedirect(reverse('mzbox:fwrules', kwargs={'client_id':fwrule.group_fk.client_fk.pk, 'group_id': fwrule.group_fk.pk}))
    else:
       form = FwRuleForm()
       for field in form.fields:
           value_text = eval("fwrule.%s" %(field))
           value_hash = {'value': value_text}
           form.fields[field].widget.__dict__['attrs'].update(value_hash) 


       return render(request, 'mzbox/fwrules_edit.html', {
           'fwrule_id': fwrule_id,
           'form': form,
           })

def fwrules_delete(request, fwrule_id):
    fwrule = Firewall_rule.objects.get(pk=fwrule_id)
    group_name = fwrule.group_fk.group_name
    client_name = fwrule.group_fk.client_fk.client_name
    fwrule.delete()

    key_name = "{}:{}:fwrules".format(client_name, group_name)
    json_fwrule = fwrules_redis_format(fwrule.group_fk.firewall_rule_set.all())
    redis_write(key_name, json_fwrule)
    run_puppet(group_name)

    return HttpResponseRedirect(reverse('mzbox:fwrules', kwargs={'client_id':fwrule.group_fk.client_fk.pk, 'group_id': fwrule.group_fk.pk}))
    

