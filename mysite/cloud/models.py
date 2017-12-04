from django.db import models
from client.models import Client

# Create your models here.

class Platform(models.Model):
    name = models.CharField(max_length=90)
    alias = models.CharField(max_length=90, default="N/A")
    description = models.CharField(max_length=100, default="N/A")

    def __str__(self):
        return self.name

class Vpc(models.Model):
    name = models.CharField(max_length=90)
    cidr_block = models.CharField(max_length=20)
    region = models.CharField(max_length=35, default="sa-east-1")
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    platform_fk = models.ForeignKey(Platform, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=100, default="N/A")
    platform_network_id = models.CharField(max_length=100, default="N/A", null=True, blank=True)

    def __str__(self):
        return self.name

class Subnet(models.Model):
    name = models.CharField(max_length=90)
    cidr_block = models.CharField(max_length=20)
    region = models.CharField(max_length=35, default="sa-east-1")
    vpc_fk = models.ForeignKey(Vpc, on_delete=models.CASCADE, default=0)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    platform_fk = models.ForeignKey(Platform, on_delete=models.CASCADE, null=True, blank=True)
    description = models.CharField(max_length=100, default="N/A")
    platform_subnet_id = models.CharField(max_length=100, default="N/A", null=True, blank=True)

    def __str__(self):
        return self.name

class SecurityGroup(models.Model):
    name = models.CharField(max_length=90)
    vpc_fk = models.ForeignKey(Vpc, on_delete=models.CASCADE, default=0)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    #platform_fk = models.ForeignKey(Platform, on_delete=models.CASCADE, default=0)
    description = models.CharField(max_length=100, default="N/A")

    def __str__(self):
        return self.name

class SecurityGroup_Rule(models.Model):
    name = models.CharField(max_length=90)
    description = models.CharField(max_length=100, default="N/A")
    securityGroup_fk = models.ForeignKey(SecurityGroup, on_delete=models.CASCADE, default=0)
    protocol = models.CharField(max_length=100)
    port = models.CharField(max_length=8)
    cidr = models.CharField(max_length=20)

    def __str__(self):
        return self.name

class CloudRole(models.Model):
    name = models.CharField(max_length=90)
    description = models.CharField(max_length=100, default="N/A")
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name

class CloudConfigurationGroup(models.Model):
    name = models.CharField(max_length=90)
    description = models.CharField(max_length=100, default="N/A")
    securityGroup_fk = models.ForeignKey(SecurityGroup, on_delete=models.CASCADE, default=0)
    vpc_fk = models.ForeignKey(Vpc, on_delete=models.CASCADE, default=0)
    subnet_fk = models.ForeignKey(Subnet, on_delete=models.CASCADE, default=0)
    cloudrole_fk = models.ForeignKey(CloudRole, on_delete=models.CASCADE, default=0)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name

class CloudInstance(models.Model):
    name = models.CharField(max_length=90)
    description = models.CharField(max_length=100, default="N/A")
    size = models.CharField(max_length=90)
    client_fk = models.ForeignKey(Client, on_delete=models.CASCADE, default=0)
    #platform_fk = models.ForeignKey(Platform, on_delete=models.CASCADE, default=0)
    cloud_cg_fk = models.ForeignKey(CloudConfigurationGroup, on_delete=models.CASCADE, default=0)

    def __str__(self):
        return self.name
