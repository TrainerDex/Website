# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-18 01:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0023_autofll_creation_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='update',
            name='meta_time_created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
