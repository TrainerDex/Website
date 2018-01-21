# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-21 15:21
from __future__ import unicode_literals

from django.db import migrations, models
import trainer.validators


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0034_auto_20180120_2104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainer',
            name='username',
            field=models.CharField(max_length=30, unique=True, validators=[trainer.validators.validate_pokemon_go_username], verbose_name='Username'),
        ),
    ]
