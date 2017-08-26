from django.db import models
from group.models import Group
from group.models import Client

class Node(models.Model):
    name = models.CharField(max_length=20)
    serial_number = models.CharField(max_length=22)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    group_fk = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    lan1_method = models.CharField(max_length=8)
    lan1_ip = models.CharField(max_length=20, null=True)
    lan1_netmask = models.CharField(max_length=20, null=True)
    lan1_gateway = models.CharField(max_length=20, null=True)
    dns1_ip = models.CharField(max_length=20)
    dns2_ip = models.CharField(max_length=20, null=True)
    dns_domain = models.CharField(max_length=30, null=True)
    dns_search = models.CharField(max_length=30, null=True)
    brand_new = models.NullBooleanField()

    def __str__(self):
        return self.name
