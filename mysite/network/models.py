from django.db import models
from group.models import Group

# Create your models here.

class Network(models.Model):
    network_name  = models.CharField(max_length=20)
    network_description = models.CharField(max_length=100, default="N/A")
    network_interface = models.CharField(max_length=7, default="N/A")
    group_fk   = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.network_name
