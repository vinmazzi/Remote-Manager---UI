import boto3

class Aws:
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')

    def delete_vpc(vpc_id):
        vpc = Aws.ec2.Vpc(vpc_id)
        igw_id = list(vpc.internet_gateways.all())[0].id
        vpc.detach_internet_gateway(InternetGatewayId = igw_id)
        igw = Aws.ec2.InternetGateway(igw_id)
        vpc.delete()
        igw.delete()

    def create_vpc(vpc_name, cidr_block, route_to_internet):
        vpc_hash = Aws.client.create_vpc(CidrBlock=cidr_block, InstanceTenancy='default')
        vpc_id = vpc_hash['Vpc']['VpcId']
        vpc = Aws.ec2.Vpc(vpc_id)
        vpc.create_tags(Tags=[{'Key': 'Name', 'Value': vpc_name}])
        if route_to_internet:
            igw = Aws.create_igw("%s_igw"%(vpc_name))
            igw.attach_to_vpc(VpcId=vpc_id)
            rt = Aws.get_vpc_route_table(vpc_id)
            rt.create_route(DestinationCidrBlock='0.0.0.0/0', GatewayId=igw.id)
        return vpc_id
    
    def create_igw(igw_name):
        igw_hash = Aws.client.create_internet_gateway()
        igw_id = igw_hash['InternetGateway']['InternetGatewayId']
        igw = Aws.ec2.InternetGateway(igw_id)
        igw.create_tags(Tags=[{'Key': 'Name', 'Value': igw_name}])
        return igw
    
    def create_subnet(vpc_id, subnet_name, cidr_block):
        subnet_id = Aws.client.create_subnet(AvailabilityZone='sa-east-1c',VpcId=vpc_id, CidrBlock=cidr_block)['Subnet']['SubnetId']
        subnet = Aws.ec2.Subnet(subnet_id)
        subnet.meta.client.modify_subnet_attribute(SubnetId=subnet_id, MapPublicIpOnLaunch={'Value': True})
        subnet.create_tags(Tags=[{'Key': 'Name', 'Value': subnet_name}])
        return subnet_id

    def create_security_group(vpc_id, sg_name, description):
        return Aws.client.create_security_group(Description=description, GroupName=sg_name, VpcId=vpc_id)['GroupId']

    def create_security_group_rule(sg_id, rule_hash):
        sg = Aws.ec2.SecurityGroup(sg_id)
        ip_permition_hash = {'FromPort': int(rule_hash['port']), 'ToPort': int(rule_hash['port']), 'IpProtocol': rule_hash['protocol'], 'IpRanges': [{'CidrIp': rule_hash['cidr'], 'Description': rule_hash['description']}]}
        sg.authorize_ingress(IpPermissions=[ip_permition_hash])

    def delete_security_group_rule(sg_id, rule_hash):
        sg = Aws.ec2.SecurityGroup(sg_id)
        ip_permition_hash = {'FromPort': int(rule_hash['port']), 'ToPort': int(rule_hash['port']), 'IpProtocol': rule_hash['protocol'], 'IpRanges': [{'CidrIp': rule_hash['cidr'], 'Description': rule_hash['description']}]}
        sg.revoke_ingress(IpPermissions=[ip_permition_hash])

    def delete_subnet(subnet_id):
        subnet = Aws.ec2.Subnet(subnet_id)
        subnet.delete()

    def delete_security_group(sg_id):
        sg = Aws.ec2.SecurityGroup(sg_id)
        sg.delete()

    def get_vpc_route_table(vpc_id):
        rts = Aws.client.describe_route_tables()
        for rt in rts['RouteTables']:
            if rt['VpcId'] == vpc_id:
                rt_id = rt['RouteTableId']
        route_table = Aws.ec2.RouteTable(rt_id)
        return route_table

class CloudActions:
    def create_network(network):
        if network.platform_fk.alias == "AWS":
            vpc_id = aws.create_vpc(network.name, network.cidr_block, true)
            return vpc_id

    def create_subnet(subnet):
        if subnet.platform_fk.alias == "AWS":
            subnet_id = Aws.create_subnet(subnet.vpc_fk.platform_network_id, subnet.name, subnet.cidr_block)
            return subnet_id

    def delete_subnet(subnet):
        if subnet.platform_fk.alias == "AWS":
            Aws.delete_subnet(subnet.platform_subnet_id)

    def delete_network(network):
        if network.platform_fk.alias == "AWS":
            Aws.delete_vpc(network.platform_network_id)

    def create_security_group(sg):
        if sg.platform_fk.alias == "AWS":
            return Aws.create_security_group(sg.vpc_fk.platform_network_id, sg.name, sg.description)

    def create_security_group_rule(sg, rule):
        if sg.platform_fk.alias == "AWS":
            return Aws.create_security_group_rule(sg.platform_sg_id, rule)

    def delete_security_group_rule(sg, rule):
        if sg.platform_fk.alias == "AWS":
            return Aws.delete_security_group_rule(sg.platform_sg_id, rule)

    def delete_security_group(sg):
        if sg.platform_fk.alias == "AWS":
            return Aws.delete_security_group(sg.platform_sg_id)
