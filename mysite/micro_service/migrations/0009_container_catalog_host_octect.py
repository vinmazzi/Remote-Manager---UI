# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-10 01:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('micro_service', '0008_container_node_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='container_catalog',
            name='host_octect',
            field=models.CharField(default='N/A', max_length=3),
        ),
    ]