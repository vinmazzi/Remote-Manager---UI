from django.db import models
from client.models import Client

# Create your models here.

class Vpc(models.Model):
    name = models.CharField(max_length=90)
    cidr_block = models.CharField(max_length=20)
    region = models.CharField(max_length=35, default="sa-east-1")
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    description = models.CharField(max_length=100, default="N/A")

    def __str__(self):
        return self.name

class Subnet(models.Model):
    name = models.CharField(max_length=90)
    cidr_block = models.CharField(max_length=20)
    region = models.CharField(max_length=35, default="sa-east-1")
    vpc_fk = models.ForeignKey(Vpc, on_delete=models.CASCADE, default=0)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    description = models.CharField(max_length=100, default="N/A")

    def __str__(self):
        return self.name

class SecurityGroup(models.Model):
    name = models.CharField(max_length=90)
    vpc_fk = models.ForeignKey(Vpc, on_delete=models.CASCADE, default=0)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    description = models.CharField(max_length=100, default="N/A")

    def __str__(self):
        return self.name

class SecurityGroup_Rule(models.Model):
    name = models.CharField(max_length=90)
    description = models.CharField(max_length=100, default="N/A")
    securityGroup_fk = models.ForeignKey(SecurityGroup, on_delete=models.CASCADE, default=0)
    protocol = models.CharField(max_length=100)
    from_port = models.CharField(max_length=8)
    to_port = models.CharField(max_length=8)
    cidr = models.CharField(max_length=20)

    def __str__(self):
        return self.name

