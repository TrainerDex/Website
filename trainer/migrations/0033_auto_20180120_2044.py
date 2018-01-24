# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-01-20 20:44
from __future__ import unicode_literals

from django.db import migrations

def rename_trainers(apps, schema_editor):
    Trainer = apps.get_model('trainer', 'Trainer')
    for trainer in Trainer.objects.all():
        if trainer.owner and (trainer.prefered==True or len(trainer.owner.profiles.all())==1) and trainer.username != trainer.owner.username:
            trainer.owner.username = trainer.username
            trainer.owner.save()

def remove_play_zones(apps, schema_editor):
    Trainer = apps.get_model('trainer', 'Trainer')
    for trainer in Trainer.objects.all():
        if len(trainer.play_zones_country.all())>=1:
            trainer.leaderboard_country = trainer.play_zones_country.first()
        if len(trainer.play_zones_region.all())>=1:
            trainer.leaderboard_region = trainer.play_zones_region.first()
        if len(trainer.play_zones_subregion.all())>=1:
            trainer.leaderboard_subregion = trainer.play_zones_subregion.first()
        if len(trainer.play_zones_city.all())>=1:
            trainer.leaderboard_city = trainer.play_zones_city.first()
        trainer.save()

class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0032_auto_20180115_1549'),
    ]

    operations = [
        migrations.RunPython(rename_trainers, reverse_code=migrations.RunPython.noop),
        migrations.RunPython(remove_play_zones, reverse_code=migrations.RunPython.noop),
    ]