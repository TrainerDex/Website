# Generated by Django 2.1.3 on 2018-12-06 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_auto_20181206_1323"),
    ]

    operations = [
        migrations.AddField(
            model_name="discordguildmembership",
            name="active",
            field=models.BooleanField(default=True),
        ),
    ]