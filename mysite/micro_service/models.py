from django.db import models
from group.models import Group
from network.models import Network
from node.models import Node

class Registry(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, default="N/A")
    url = models.CharField(max_length=100)
    port = models.CharField(max_length=5, default="5000")
    user = models.CharField(max_length=20, blank=True, null=True)
    password = models.CharField(max_length=30, blank=True, null=True)
    email = models.CharField(max_length=50, blank=True, null=True)
    ca_crt = models.CharField(max_length=5000, blank=True, null=True)
    group_fk = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name

class Image(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, default="N/A")
    group_fk   = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)
    registry_fk   = models.ForeignKey(Registry, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name

class Container_catalog(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100, default="N/A")
    group_fk   = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)
    network_fk = models.ForeignKey(Network, on_delete=models.CASCADE, default=0)
    image_name = models.CharField(max_length=100, default="N/A") 
    host_octect = models.CharField(max_length=3, default="N/A")
    registry_fk   = models.ForeignKey(Registry, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name

class Container(models.Model):
    container_catalog_fk = models.ForeignKey(Container_catalog, on_delete=models.CASCADE, default=0)
    ipaddress = models.CharField(max_length=20, default="N/A")
    node_fk = models.ForeignKey(Node, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.container_catalog_fk.name
