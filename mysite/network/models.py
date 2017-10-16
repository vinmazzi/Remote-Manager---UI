from django.db import models
from group.models import Group
from node.models import Node

# Create your models here.

class Network(models.Model):
    network_name  = models.CharField(max_length=20)
    network_bridge = models.BooleanField(default=False)
    network_default_gateway = models.BooleanField(default=False)
    network_bridge_name = models.CharField(max_length=20, default="N/A") 
    network_description = models.CharField(max_length=100, default="N/A")
    network_interface = models.CharField(max_length=7, default="N/A")
    group_fk   = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.network_name

class Interface(models.Model):
    ipaddress  = models.CharField(max_length=20, null=True)
    method   = models.CharField(max_length=20)
    netmask  = models.CharField(max_length=20, null=True)
    bridge = models.BooleanField(default=False)
    gateway  = models.CharField(max_length=20, null=True)
    network_fk = models.ForeignKey(Network, on_delete=models.CASCADE, default=0)
    node_fk = models.ForeignKey(Node, on_delete=models.CASCADE, default=0)
    
    def __str__(self):
        return self.network_fk.network_interface
