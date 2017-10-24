from django.db import models
from group.models import Group
from network.models import Interface

# Create your models here.

class Route(models.Model):
    network  = models.CharField(max_length=20)
    interface_fk = models.ForeignKey(Interface, on_delete=models.CASCADE, default=0)
    gateway  = models.CharField(max_length=20)
    netmask  = models.CharField(max_length=20, default="255.255.255.0")

    def __str__(self):
        return self.network
