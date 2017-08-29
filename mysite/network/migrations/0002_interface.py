# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-28 20:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0007_node_brand_new'),
        ('network', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Interface',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.CharField(max_length=20, null=True)),
                ('method', models.CharField(max_length=20)),
                ('netmask', models.CharField(max_length=20, null=True)),
                ('gateway', models.CharField(max_length=20, null=True)),
                ('network_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='network.Network')),
                ('node_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='node.Node')),
            ],
        ),
    ]
