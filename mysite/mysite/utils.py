import redis

class Utils:
    def redis_write(key_name, value):
       host_ip = "192.168.122.132"
       tcp_port = 6379
       try:
           rc = redis.StrictRedis(host=host_ip, port=tcp_port, db=0)
           rc.set(key_name, value)
       except Exception as err:
           return HttpResponse(err)
