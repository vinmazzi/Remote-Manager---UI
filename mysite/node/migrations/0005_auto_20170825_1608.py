# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-25 19:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('node', '0004_auto_20170825_1607'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='group_fk',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group'),
        ),
    ]
