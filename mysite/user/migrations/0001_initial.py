# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-09-21 20:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('client', '0002_client_client_alias'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserExtraInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='client.Client')),
                ('user_fk', models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]