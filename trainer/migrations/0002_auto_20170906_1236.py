# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-09-06 12:36
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Discord_Relations',
            new_name='Discord_Relation',
        ),
        migrations.RenameModel(
            old_name='Discord_Servers',
            new_name='Discord_Server',
        ),
        migrations.RenameModel(
            old_name='Discord_Users',
            new_name='Discord_User',
        ),
        migrations.RenameModel(
            old_name='Factions',
            new_name='Faction',
        ),
        migrations.RenameModel(
            old_name='Trainer_Levels',
            new_name='Trainer_Level',
        ),
        migrations.RenameModel(
            old_name='Experience',
            new_name='Update',
        ),
    ]
