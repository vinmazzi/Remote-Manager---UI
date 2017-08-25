from django.db import models
from django.utils import timezone
from client.models import Client
from group.models import Group

import datetime

class Firewall_rule(models.Model):
    group_fk       = models.ForeignKey(Group, on_delete=models.CASCADE, default=0)
    rule_name_text = models.CharField(max_length=150)
    source         = models.CharField(max_length=20, blank=True, null=True)
    destination    = models.CharField(max_length=20, blank=True, null=True)
    proto          = models.CharField(max_length=7, blank=True, null=True)
    chain          = models.CharField(max_length=15, blank=True, null=True)
    action         = models.CharField(max_length=11, blank=True, null=True)
    table          = models.CharField(max_length=10, blank=True, null=True)
    outiface       = models.CharField(max_length=10, blank=True, null=True)
    iniface        = models.CharField(max_length=10, blank=True, null=True)
    sport          = models.IntegerField(default=0, blank=True, null=True)
    dport          = models.IntegerField(default=0, blank=True, null=True)

    def __str__(self):
        return self.rule_name_text
