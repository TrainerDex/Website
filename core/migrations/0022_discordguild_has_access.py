# Generated by Django 2.1.11 on 2019-11-12 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20191108_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='discordguild',
            name='has_access',
            field=models.BooleanField(default=False),
        ),
    ]
