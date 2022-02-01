# Generated by Django 2.2.17 on 2020-11-27 01:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pokemongo", "0045_battle_hub_stats"),
    ]

    operations = [
        migrations.AlterField(
            model_name="update",
            name="total_xp",
            field=models.PositiveIntegerField(
                blank=True, null=True, verbose_name="Total XP"
            ),
        ),
    ]