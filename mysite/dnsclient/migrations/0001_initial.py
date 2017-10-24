# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-13 14:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0002_auto_20170822_1530'),
    ]

    operations = [
        migrations.CreateModel(
            name='DnsClient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('domain', models.CharField(max_length=260)),
                ('search', models.CharField(max_length=260)),
                ('dns1_address', models.CharField(max_length=20)),
                ('dns2_address', models.CharField(max_length=20)),
                ('group_fk', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
            ],
        ),
    ]