# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-10-05 21:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('group', '0002_auto_20170822_1530'),
        ('network', '0005_network_network_bridge_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(default='N/A', max_length=100)),
                ('group_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
            ],
        ),
        migrations.CreateModel(
            name='Micro_service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(default='N/A', max_length=100)),
                ('ipaddress', models.CharField(default='N/A', max_length=17)),
                ('group_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
                ('image_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='micro_service.Image')),
                ('network_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='network.Network')),
            ],
        ),
        migrations.CreateModel(
            name='Registry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
                ('description', models.CharField(default='N/A', max_length=100)),
                ('url', models.CharField(max_length=100)),
                ('port', models.CharField(default='5000', max_length=5)),
                ('group_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='group.Group')),
            ],
        ),
        migrations.AddField(
            model_name='image',
            name='registry_fk',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='micro_service.Registry'),
        ),
    ]
