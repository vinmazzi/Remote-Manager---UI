# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 15:48
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dnsclient', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dnsclient',
            name='search',
        ),
    ]
