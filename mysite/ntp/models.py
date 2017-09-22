from django.db import models

# Create your models here.
from group.models import Group
class Ntp(models.Model):
    group_fk = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)
    servers  = models.CharField(max_length=46)
