# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-12-17 16:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0013_auto_20171212_2259'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='discordguild',
            name='maintainer',
        ),
        migrations.DeleteModel(
            name='DiscordGuild',
        ),
    ]
