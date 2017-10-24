# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-14 00:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0006_network_network_default_gateway'),
        ('route', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='route',
            name='group_fk',
        ),
        migrations.RemoveField(
            model_name='route',
            name='network_fk',
        ),
        migrations.AddField(
            model_name='route',
            name='interface_fk',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='network.Interface'),
        ),
        migrations.AddField(
            model_name='route',
            name='netmask',
            field=models.CharField(default='255.255.255.0', max_length=20),
        ),
    ]
