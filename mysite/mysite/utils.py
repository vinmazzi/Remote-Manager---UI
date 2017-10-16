import redis, paramiko, json, requests
from django.http import HttpResponse, HttpResponseRedirect

class Utils:
    def razor_write(data_json, command):
       url = "http://192.168.1.102:8150/api/commands/{}".format(command)
       #json_data = json.dumps({'name':'teste2', 'rule': ["=",["fact","serialnumber"],"MeuSerialEEETRYHS-44"]})
       r = requests.post(url, data=data_json, headers={'Content-Type':'application/json'})
       return r

    def redis_write(key_name, value):
       host_ip = "192.168.1.201"
       tcp_port = 6379
       try:
           rc = redis.StrictRedis(host=host_ip, port=tcp_port, db=0)
           rc.set(key_name, value)
       except Exception as err:
           return HttpResponse(err)

    def run_puppet(group_name):
       ssh = paramiko.SSHClient()
       try:
           ssh.load_system_host_keys()
           ssh.connect('192.168.1.201', username="mcollective", password="mcollective")
           stdin, stdout,stder = ssh.exec_command("/opt/puppetlabs/bin/mco puppet runonce -F group_name={}".format(group_name))
           ssh.close
       except Exception as err:
           return HttpResponse(err)

    def single_container_redis_format(containers):
        host_containers = {}
        if containers:
            for container in containers:
                node = container.node_fk
                if "redis_key" not in host_containers.keys():
                    host_containers = {'redis_key': "{}:{}:containers".format(node.client_fk.client_name, node.name)}
                network_name = container.container_catalog_fk.network_fk.network_name
                network_ip = container.ipaddress
                image_name = container.container_catalog_fk.image_name
                container_name = container.container_catalog_fk.name.replace(" ", "_")
                registry = "{}:{}".format(container.container_catalog_fk.registry_fk.url, container.container_catalog_fk.registry_fk.port)
                container_hash_tmp = {container_name: {
                        'image': "%s/%s:latest" %(registry,image_name),
                        'ipaddress': network_ip,
                        'network': network_name,
                       }}
                host_containers.update(container_hash_tmp)
        redis_key = host_containers['redis_key']
        host_containers.pop('redis_key')
        redis_value = json.dumps(host_containers)
        Utils.redis_write(redis_key, redis_value)

    def create_certificate(node_name):
       ssh = paramiko.SSHClient()
       try:
           ssh.load_system_host_keys()
           ssh.connect('104.236.61.57', username="vpn", password="ImM@zzi..0256")
           stdin, stdout,stder = ssh.exec_command("cd /etc/openvpn/easy-rsa; source vars; sudo -E ./build-key {0}; cd keys; sudo ln -s {0}.crt {0}_crt; sudo ln -s {0}.key {0}_key".format(node_name))
           ssh.close
       except Exception as err:
           return HttpResponse(err)
