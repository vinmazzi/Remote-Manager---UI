from django.db import models
from client.models import Client

# Create your models here.

class Group(models.Model):
    group_name  = models.CharField(max_length=20)
    group_alias = models.CharField(max_length=20, default="N/A")
    group_description = models.CharField(max_length=100, default="N/A")
    client_fk   = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.group_name
