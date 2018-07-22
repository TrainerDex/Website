# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-22 12:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0056_auto_20180714_1359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='update',
            name='meta_source',
            field=models.CharField(choices=[('?', None), ('cs_social_twitter', 'Twitter (Found)'), ('cs_social_facebook', 'Facebook (Found)'), ('cs_social_youtube', 'YouTube (Found)'), ('cs_?', 'Sourced Elsewhere'), ('ts_social_discord', 'Discord'), ('ts_social_twitter', 'Twitter'), ('ts_direct', 'Directly told (via text)'), ('web_quick', 'Quick Update (Web)'), ('web_detailed', 'Detailed Update (Web)'), ('ts_registration', 'Registration'), ('ss_registration', 'Registration w/ Screenshot'), ('ss_generic', 'Generic Screenshot'), ('ss_ocr', 'OCR Screenshot'), ('com.nianticlabs.pokemongo.friends', 'In Game Friends'), ('com.pokeassistant.trainerstats', 'Poké Assistant'), ('com.pokenavbot.profiles', 'PokeNav'), ('tl40datateam.spreadsheet', 'Tl40 Data Team')], default='?', max_length=256, verbose_name='Source'),
        ),
    ]