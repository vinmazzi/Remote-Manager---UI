# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-22 15:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('client', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('group_name', models.CharField(max_length=20)),
                ('client_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='client.Client')),
            ],
        ),
    ]
