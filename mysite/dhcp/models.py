from django.db import models
from group.models import Group
from network.models import Interface
from network.models import Network

# Create your models here.

class Dhcp_service(models.Model):
    group_fk = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)
    nameservers = models.CharField(max_length=150)
    ntpservers = models.CharField(max_length=150)
    interfaces = models.CharField(max_length=150)
    pxeserver = models.CharField(max_length=150)
    pxefilename = models.CharField(max_length=150, default="pxelinux.0")
    dnsdomain = models.CharField(max_length=150, default="N/A")

class Dhcp_pool(models.Model):
    interface_fk = models.ForeignKey(Interface, on_delete=models.CASCADE, default=0)
    mask = models.CharField(max_length=150)
    domain = models.CharField(max_length=150, default="N/A")
    network = models.CharField(max_length=150, default="N/A")
    network_range = models.CharField(max_length=150)
    gateway = models.CharField(max_length=150)
