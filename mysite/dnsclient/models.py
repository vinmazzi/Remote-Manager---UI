from django.db import models
from group.models import Group

# Create your models here.

class DnsClient(models.Model):
    domain = models.CharField(max_length=260)
    dns1_address = models.CharField(max_length=20)
    dns2_address = models.CharField(max_length=20)
    group_fk = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.domain
