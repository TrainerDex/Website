# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-03-28 12:05
from __future__ import unicode_literals

from django.db import migrations, models
import trainer.models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0045_auto_20180322_1442'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainer',
            name='active',
        ),
        migrations.AddField(
            model_name='trainer',
            name='verification',
            field=models.ImageField(blank=True, null=True, upload_to=trainer.models.VerificationImagePath),
        ),
        migrations.AddField(
            model_name='update',
            name='image_proof',
            field=models.ImageField(blank=True, null=True, upload_to=trainer.models.VerificationUpdateImagePath),
        ),
    ]
