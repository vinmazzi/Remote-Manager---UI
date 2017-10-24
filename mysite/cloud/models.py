from django.db import models
from client.models import Client

# Create your models here.

class Vpc(models.Model):
    name = models.CharField(max_length=20)
    cidr_block = models.CharField(max_length=20)
    region = models.CharField(max_length=35, default="sa-east-1")
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name

class Subnet(models.Model):
    name = models.CharField(max_length=20)
    cidr_block = models.CharField(max_length=20)
    region = models.CharField(max_length=35, default="sa-east-1")
    vpc_fk = models.ForeignKey(Vpc, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name
