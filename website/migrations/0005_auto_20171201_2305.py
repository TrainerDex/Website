# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-01 23:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_auto_20171201_2251'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basecommunity',
            name='locations',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='cities_light.City'),
        ),
    ]
