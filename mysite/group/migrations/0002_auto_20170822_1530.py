# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 18:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('group', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='group_alias',
            field=models.CharField(default='N/A', max_length=20),
        ),
        migrations.AddField(
            model_name='group',
            name='group_description',
            field=models.CharField(default='N/A', max_length=100),
        ),
    ]