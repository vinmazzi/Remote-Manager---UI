# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-06 14:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('micro_service', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='registry',
            name='email',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='registry',
            name='password',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
        migrations.AddField(
            model_name='registry',
            name='user',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]
