from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from client.models import Client
from group.models import Group
from django.forms.models import model_to_dict
import redis, ast, json, paramiko, boto3
from .forms import VpcForm, SubnetForm, SecurityGroupForm, CloudConfigurationGroupForm, CloudInstanceForm
from .models import Platform, Vpc, Subnet, SecurityGroup, SecurityGroup_Rule, CloudConfigurationGroup, CloudRole, CloudInstance
from .cloud_actions import CloudActions
from mysite.utils import Utils

# Create your views here.

def vpc_redis_format(vpcs, client):
    vpc_hash = {}
    for vpc in vpcs:
        tmp_name = vpc.name
        pop_keys = ['name', 'id', 'client_fk', 'description']
        dict_vpc = model_to_dict(vpc)
        for pop in pop_keys:
            dict_vpc.pop(pop)
        tmp_format = ast.literal_eval("{\'%s\': %s}" %(tmp_name, dict_vpc))
        vpc_hash.update(tmp_format)
    key_name = "common:{}:cloud:vpcs".format(client.client_name.lower())
    json_vpc_hash = json.dumps(vpc_hash)
    Utils.redis_write(key_name, json_vpc_hash)

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
    json_subnet_hash = json.dumps(subnet_hash)
    Utils.redis_write(key_name, json_subnet_hash)

def sg_redis_format(sgs, client):
    sgs_hash = {}
    for sg in sgs:
        sg_dict = model_to_dict(sg)
        region = sg.vpc_fk.region
        vpc = sg.vpc_fk.name
        description = sg.description
        name = sg.name
        pop_rule_options = ['id', 'name', 'securityGroup_fk', 'description']
        if sg.securitygroup_rule_set.all():
            ingress_list = []
            for rule in sg.securitygroup_rule_set.all():
                rule_dict = model_to_dict(rule)
                for pop in pop_rule_options:
                    rule_dict.pop(pop)
                ingress_list.append(rule_dict)
            sg_hash = {name: {"region": region, "vpc": vpc, "description": description, "ingress": ingress_list}}
        else:
            sg_hash = {name: {'region': region, 'vpc': vpc, 'description': description}}
        sgs_hash.update(sg_hash)
    key_name = "common:{}:cloud:sgs".format(client.client_name.lower())
    json_sgs_hash = json.dumps(sgs_hash)
    Utils.redis_write(key_name, json_sgs_hash)

def instance_redis_format(instances, client):
    instances_hash = {}
    for instance in instances:
        region = instance.cloud_cg_fk.vpc_fk.region
        subnet = instance.cloud_cg_fk.subnet_fk.name
        security_groups = instance.cloud_cg_fk.securityGroup_fk.name
        image_id = 'ami-a789ffcb'
        instance_type = instance.size
        name = instance.name
        key_name = 'vmazzi'
        instance_hash = {name: {'region': region, 'image_id': image_id, 'instance_type': instance_type, 'key_name': key_name, 'subnet': subnet, 'security_groups': [security_groups]}}
        instances_hash.update(instance_hash)
    key_name = "common:{}:cloud:instances".format(client.client_name.lower())
    json_instances_hash = json.dumps(instances_hash)
    Utils.redis_write(key_name, json_instances_hash)

def cloud_options(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    return render(request, "cloud/cloud_options.html")

def vpc_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    ec2_client = boto3.client('ec2')
    if request.method == "POST":
        form = VpcForm(request.POST)
        platform = Platform.objects.get(pk=request.POST.get('platform'))
        if form.is_valid():
            network = client.vpc_set.create(
                        name = form.cleaned_data['name'],
                        cidr_block = form.cleaned_data['cidr_block'],
                        platform_fk = platform,
                        description = form.cleaned_data['description'],
                    )
            platform_network_id = CloudActions.create_network(network)
            network.platform_network_id = platform_network_id
            network.save()
        return HttpResponseRedirect(reverse('cloud:vpc_list'))
    vpcs = client.vpc_set.all()
    platforms = Platform.objects.all()
    form = VpcForm()
    vpcs_hash = ec2_client.describe_vpcs()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description' or field == 'ca_crt'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
    return render(request, 'cloud/cloud_vpc_list.html', {
        'form': form,
        'vpcs': vpcs,
        'platforms': platforms,
        'vpcs_hash': json.dumps(vpcs_hash),
        })

def vpc_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    vpc = Vpc.objects.get(pk=request.POST.get('vpc_id'))
    CloudActions.delete_network(vpc)
    vpc.delete()
    return HttpResponseRedirect(reverse('cloud:vpc_list'))

def vpc_edit(request, vpc_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    vpc = Vpc.objects.get(pk=vpc_id)
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        vpc.name = request.POST.get('modal_vpc_name')
        vpc.description = request.POST.get('modal_vpc_description')
        vpc.cidr_block = request.POST.get('modal_vpc_network')
        vpc.region = request.POST.get('modal_vpc_region')
        vpc.save()
        vpcs = client.vpc_set.all()
        key_name = "common:{}:cloud:vpcs".format(client.client_name.lower())
        vpc_redis_format(vpcs, client)
        return HttpResponseRedirect(reverse('cloud:vpc_list'))
    return HttpResponse(json.dumps(model_to_dict(vpc)), content_type="application/json")


def subnet_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    vpcs = client.vpc_set.all()
    platforms = Platform.objects.all()
    if request.method == 'POST':
        form = SubnetForm(request.POST)
        vpc = Vpc.objects.get(pk=request.POST.get('vpc'))
        platform = Platform.objects.get(pk=request.POST.get('platform'))
        if form.is_valid():
           subnet = vpc.subnet_set.create(
                        name = form.cleaned_data['name'],
                        cidr_block = form.cleaned_data['cidr_block'],
                        description = form.cleaned_data['description'],
                        client_fk = vpc.client_fk,
                        platform_fk = platform,
                    )
           subnet_aws = CloudActions.create_subnet(subnet)
           subnet.platform_subnet_id = subnet_aws
           subnet.save()
        return HttpResponseRedirect(reverse('cloud:subnet_list'))
    subnets = client.subnet_set.all()
    form = SubnetForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description' or field == 'ca_crt'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
    return render(request, 'cloud/cloud_subnet_list.html', {
            'form': form,
            'platforms': platforms,
            'subnets': subnets,
        })

def get_vpcs_by_platform(request, platform_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    platform = Platform.objects.get(id=platform_id)
    vpcs = Vpc.objects.filter(platform_fk=platform)
    vpc_hash = {}
    for vpc in vpcs:
        vpc_hash.update({vpc.name: vpc.pk})
    return HttpResponse(json.dumps(vpc_hash), content_type="application/json")

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

def fwrule_group_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    sg_id = request.POST.get('sg_id')
    sg = SecurityGroup.objects.get(pk=sg_id) 
    client = sg.client_fk
    sg.delete()
    sgs = client.securitygroup_set.all()
    sg_redis_format(sgs, client)
    return HttpResponseRedirect(reverse('cloud:fwrule_group_list'))

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

def fwrule_group_rule_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    rule_id = request.body.decode('utf8').split('=')[1]
    rule = SecurityGroup_Rule.objects.get(pk=rule_id) 
    client = rule.securityGroup_fk.client_fk
    rule.delete()
    sgs = client.securitygroup_set.all()
    sg_redis_format(sgs, client)
    ret = {'ret': 'OK'}
    return HttpResponse(json.dumps(ret), content_type="application/json")

def fwrule_group_rule_create(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    request = request.body.decode('utf8')
    rule_hash = eval(request)
    sg = SecurityGroup.objects.get(pk=rule_hash['sg_id'])
    client = sg.client_fk
    sg.securitygroup_rule_set.create(
                name = rule_hash['description'],   
                description = rule_hash['description'],   
                protocol = rule_hash['protocol'],   
                port = rule_hash['port_range'],   
                cidr = rule_hash['source'],   
            )
    ret = {'ret': request}
    sgs = client.securitygroup_set.all()
    sg_redis_format(sgs, client)
    return HttpResponse(json.dumps(ret), content_type="application/json")

def configuration_group_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    if request.method == "POST":
        form = SecurityGroupForm(request.POST) 
        vpc = Vpc.objects.get(pk=request.POST.get('vpc'))
        subnet = Subnet.objects.get(pk=request.POST.get('subnet'))
        role = CloudRole.objects.get(pk=request.POST.get('role'))
        sg = SecurityGroup.objects.get(pk=request.POST.get('sg'))
        if form.is_valid():
            client.cloudconfigurationgroup_set.create(
                        name = form.cleaned_data['name'],
                        vpc_fk = vpc,
                        securityGroup_fk = sg,
                        subnet_fk = subnet,
                        cloudrole_fk = role,
                        description = form.cleaned_data['description'],
            )
    configurations = CloudConfigurationGroup.objects.filter(client_fk=client)
    vpcs = client.vpc_set.all()
    form = CloudConfigurationGroupForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
    return render(request, 'cloud/cloud_configuration_group_lits.html', {
            'form': form,
            'vpcs': vpcs,
            'configurations': configurations,
        })

def configuration_group_edit(request, cg_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    cg = CloudConfigurationGroup.objects.get(pk=cg_id)
    if request.method == 'POST':
        cg.name = request.POST.get("modal_configuration_name")
        cg.description = request.POST.get("modal_configuration_description")
        cg.vpc_fk = Vpc.objects.get(pk=request.POST.get("modal_configuration_vpc"))
        cg.subnet_fk = Subnet.objects.get(pk=request.POST.get("modal_configuration_subnet"))
        cg.securityGroup_fk = SecurityGroup.objects.get(pk=request.POST.get("modal_configuration_sg"))
        cg.role_fk = CloudRole.objects.get(pk=request.POST.get("modal_configuration_role"))
        cg.save()
        return HttpResponseRedirect(reverse('cloud:configuration_group_list'))
    return HttpResponse(json.dumps(model_to_dict(cg)), content_type="application/json")

def configuration_group_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    cg = CloudConfigurationGroup.objects.get(pk=request.POST.get('configuration_id'))
    cg.delete()
    return HttpResponseRedirect(reverse('cloud:configuration_group_list'))


def subnets_sgs_roles(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    vpc_id = eval(request.body.decode('utf8'))['vpc_id']
    vpc = Vpc.objects.get(pk=int(vpc_id))
    client = vpc.client_fk
    sgs = vpc.securitygroup_set.all()
    subnets = vpc.subnet_set.all()
    roles = client.cloudrole_set.all()
    obj_hash = {'sgs':{}, 'subnets':{}, 'roles': {}}
    for sg in sgs:
        tmp_hash = {sg.name: {'id': sg.pk}}
        obj_hash['sgs'].update(tmp_hash)
    for subnet in subnets:
        tmp_hash = {subnet.name: {'id': subnet.pk}}
        obj_hash['subnets'].update(tmp_hash)
    for role in roles:
        tmp_hash = {role.name: {'id': role.pk}}
        obj_hash['roles'].update(tmp_hash)
    return HttpResponse(json.dumps(obj_hash), content_type="application/json")

def instance_list(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    cloud_cgs = CloudConfigurationGroup.objects.filter(client_fk=client)
    if request.method == 'POST':
        instance_size = request.POST.get('size')
        cloud_cg = CloudConfigurationGroup.objects.get(pk=request.POST.get('cloud_cg'))
        form = CloudInstanceForm(request.POST)
        if form.is_valid():
            client.cloudinstance_set.create(
                        name = form.cleaned_data['name'],
                        description = form.cleaned_data['description'],
                        cloud_cg_fk = cloud_cg,
                        size = instance_size,
                    )
            instances = CloudInstance.objects.filter(client_fk=client)
            instance_redis_format(instances, client)
        return HttpResponseRedirect(reverse('cloud:instance_list'))
    instances = CloudInstance.objects.filter(client_fk=client)
    form = CloudInstanceForm()
    for field in form.fields:
        form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control'})
        if (field == 'description'):
            form.fields[field].widget.__dict__['attrs'].update({'class': 'form-control autogrow'})
    return render(request, 'cloud/cloud_instance_list.html', {
            'form': form,
            'cloud_cgs': cloud_cgs,
            'instances': instances,
        })

def instance_delete(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login:index'))
    client_id = request.session.get('client_id')
    client = Client.objects.get(pk=client_id)
    instance = CloudInstance.objects.get(pk=request.POST.get('instance_id'))
    instance.delete()
    instances = CloudInstance.objects.filter(client_fk=client)
    instance_redis_format(instances, client)
    return HttpResponseRedirect(reverse('cloud:instance_list'))
