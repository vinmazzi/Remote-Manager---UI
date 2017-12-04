# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-30 20:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cloud', '0010_cloudrole_client_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='cloudconfigurationgroup',
            name='cloudrole_fk',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='cloud.CloudRole'),
        ),
    ]