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

    def delete_network(network):
        if network.platform_fk.alias == "AWS":
            Aws.delete_vpc(network.platform_network_id)

