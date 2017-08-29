import redis, paramiko

class Utils:
    def redis_write(key_name, value):
       host_ip = "192.168.122.132"
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
           ssh.connect('192.168.122.132', username="mcollective", password="mcollective")
           stdin, stdout,stder = ssh.exec_command("/opt/puppetlabs/bin/mco puppet runonce -F group_name={}".format(group_name))
           ssh.close
       except Exception as err:
           return HttpResponse(err)
