from django.db import models
from group.models import Group
from group.models import Client

class Store(models.Model):
    name = models.CharField(max_length=30, default="N/A")
    code = models.CharField(max_length=6)
    country = models.CharField(max_length=40)
    state = models.CharField(max_length=40)
    city = models.CharField(max_length=40)
    address = models.CharField(max_length=40)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    group_fk = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.code
