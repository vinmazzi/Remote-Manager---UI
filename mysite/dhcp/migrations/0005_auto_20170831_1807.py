# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-31 21:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('network', '0003_auto_20170828_2052'),
        ('dhcp', '0004_auto_20170831_1801'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dhcp_pool',
            name='network_fk',
        ),
        migrations.RemoveField(
            model_name='dhcp_pool',
            name='node_fk',
        ),
        migrations.AddField(
            model_name='dhcp_pool',
            name='interface_fk',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='network.Interface'),
        ),
    ]
