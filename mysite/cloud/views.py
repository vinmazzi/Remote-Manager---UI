from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from client.models import Client
from group.models import Group
from django.forms.models import model_to_dict
import redis, ast, json, paramiko
from .forms import VpcForm, SubnetForm, SecurityGroupForm
from .models import Vpc, Subnet, SecurityGroup
from mysite.utils import Utils

# Create your views here.

def vpc_redis_format(vpcs):
    vpc_hash = {}
    for vpc in vpcs:
        tmp_name = vpc.name
        pop_keys = ['name', 'id', 'client_fk', 'description', 'vpc_fk']
        dict_vpc = model_to_dict(vpc)
        for pop in pop_keys:
            dict_vpc.pop(pop)
        tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_name, dict_vpc))
        vpc_hash.update(tmp_format)
    key_name = "common:{}:cloud:vpcs".format(client.client_name.lower())
    Utils.redis_write(key_name, vpcs_hash)

def subnet_redis_format(subnets, client):
    subnet_hash = {}
    for subnet in subnets:
        tmp_name = subnet.name
        vpc_name = subnet.vpc_fk.name
        pop_keys = ['name', 'id', 'client_fk', 'description', 'vpc_fk']
        dict_subnet = model_to_dict(subnet)
        dict_subnet.update({'vpc': vpc_name})
        for pop in pop_keys:
            dict_subnet.pop(pop)
        tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_name, dict_subnet))
        subnet_hash.update(tmp_format)
    key_name = "common:{}:cloud:subnets".format(client.client_name.lower())
    Utils.redis_write(key_name, subnet_hash)

def cloud_options(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    return render(request, "cloud/cloud_options.html")

def vpc_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        form = VpcForm(request.POST)
        if form.is_valid():
            client.vpc_set.create(
                        name = form.cleaned_data['name'],
                        cidr_block = form.cleaned_data['cidr_block'],
                        region = form.cleaned_data['region'],
                        description = form.cleaned_data['description'],
                    )
        vpcs = client.vpc_set.all()
        key_name = "common:{}:cloud:vpcs".format(client.client_name.lower())
        vpcs_hash = vpc_redis_format(vpcs)
        Utils.redis_write(key_name, vpcs_hash)
        return HttpResponseRedirect(reverse('cloud:vpc_list'))
    vpcs = client.vpc_set.all()
    form = VpcForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description' or field == 'ca_crt'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
    return render(request, 'cloud/cloud_vpc_list.html', {
        'form': form,
        'vpcs': vpcs,
        })

def vpc_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    vpc = Vpc.objects.get(pk=request.POST.get('vpc_id'))
    vpc.delete()
    vpcs = client.vpc_set.all()
    key_name = "common:{}:cloud:vpcs".format(client.client_name.lower())
    vpcs_hash = vpc_redis_format(vpcs)
    Utils.redis_write(key_name, vpcs_hash)
    return HttpResponseRedirect(reverse('cloud:vpc_list'))

def vpc_edit(request, vpc_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    vpc = Vpc.objects.get(pk=vpc_id)
    if request.method == "POST":
        vpc.name = request.POST.get('modal_vpc_name')
        vpc.description = request.POST.get('modal_vpc_description')
        vpc.cidr_block = request.POST.get('modal_vpc_network')
        vpc.region = request.POST.get('modal_vpc_region')
        vpc.save()
        vpcs = client.vpc_set.all()
        key_name = "common:{}:cloud:vpcs".format(client.client_name.lower())
        vpcs_hash = vpc_redis_format(vpcs)
        Utils.redis_write(key_name, vpcs_hash)
        return HttpResponseRedirect(reverse('cloud:vpc_list'))
    return HttpResponse(json.dumps(model_to_dict(vpc)), content_type="application/json")


def subnet_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    vpcs = client.vpc_set.all()
    if request.method == 'POST':
        form = SubnetForm(request.POST)
        vpc = Vpc.objects.get(pk=request.POST.get('vpc'))
        if form.is_valid():
            vpc.subnet_set.create(
                        name = form.cleaned_data['name'],
                        cidr_block = form.cleaned_data['cidr_block'],
                        description = form.cleaned_data['description'],
                        region = vpc.region,
                        client_fk = vpc.client_fk,

                    )
        else:
            return HttpResponse(form)
        subnets = client.subnet_set.all()
        subnets_hash = subnet_redis_format(subnets, client)
        return HttpResponseRedirect(reverse('cloud:subnet_list'))
    subnets = client.subnet_set.all()
    form = SubnetForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description' or field == 'ca_crt'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
    return render(request, 'cloud/cloud_subnet_list.html', {
            'form': form,
            'vpcs': vpcs,
            'subnets': subnets,
        })

def subnet_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    subnet = Subnet.objects.get(pk=request.POST.get('subnet_id'))
    client = subnet.client_fk
    subnet.delete()
    subnets = client.subnet_set.all()
    subnet_redis_format(subnets, client)
    return HttpResponseRedirect(reverse('cloud:subnet_list'))

def subnet_edit(request, subnet_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    subnet = Subnet.objects.get(pk=subnet_id)
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        vpc = Vpc.objects.get(pk=request.POST.get('modal_subnet_vpc'))
        subnet.name = request.POST.get('modal_subnet_name')
        subnet.description = request.POST.get('modal_subnet_description')
        subnet.cidr_block = request.POST.get('modal_subnet_network')
        subnet.vpc_fk = vpc
        subnet.save()
        subnets = client.subnet_set.all()
        subnet_redis_format(subnets, client)
        return HttpResponseRedirect(reverse('cloud:subnet_list'))
    return HttpResponse(json.dumps(model_to_dict(subnet)), content_type="application/json")

def fwrule_group_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    if request.method == "POST":
        vpc = Vpc.objects.get(pk=request.POST.get('vpc'))
        form = SecurityGroupForm(request.POST) 
        if form.is_valid():
            vpc.securitygroup_set.create(
                        name = form.cleaned_data['name'],
                        vpc_fk = vpc,
                        client_fk = vpc.client_fk,
                        description = form.cleaned_data['description'],
                    )
    form = SecurityGroupForm()
    vpcs = Vpc.objects.all()
    sgs = SecurityGroup.objects.all()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description' or field == 'ca_crt'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
    return render(request, 'cloud/cloud_sg_list.html', {
            'form': form,
            'vpcs': vpcs,
            'sgs': sgs,
        })

def fwrule_group_edit(request, sg_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    sg = SecurityGroup.objects.get(pk=sg_id)
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        vpc = Vpc.objects.get(pk=request.POST.get('modal_sg_vpc'))
        sg.name = request.POST.get('modal_sg_name')
        sg.description = request.POST.get('modal_sg_description')
        sg.vpc_fk = vpc
        sg.save()
       # sgs = client.sg_set.all()
       # sg_redis_format(sgs, client)
        return HttpResponseRedirect(reverse('cloud:fwrule_group_list'))
    return HttpResponse(json.dumps(model_to_dict(sg)), content_type="application/json")

def fwrule_group_rule_edit(request, sg_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    sg = SecurityGroup.objects.get(pk=sg_id)
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    rules = sg.securitygroup_rule_set.all()
    rules_hash = {}
    for rule in rules:
       rule_hash = model_to_dict(rule)
       rule_id = rule_hash['id']
       rule_hash.pop('id')
       tmp_format = ast.literal_eval("{\'%s\': %s}" %(rule_id, rule_hash))
       rules_hash.update(tmp_format)
    return HttpResponse(json.dumps(rules_hash), content_type="application/json")
