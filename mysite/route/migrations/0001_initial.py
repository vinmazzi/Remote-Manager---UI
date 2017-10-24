# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 23:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0002_auto_20170822_1530'),
        ('network', '0006_network_network_default_gateway'),
    ]

    operations = [
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('network', models.CharField(max_length=20)),
                ('gateway', models.CharField(max_length=20)),
                ('group_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
                ('network_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='network.Network')),
            ],
        ),
    ]
