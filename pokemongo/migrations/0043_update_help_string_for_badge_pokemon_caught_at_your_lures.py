# Generated by Django 2.2.17 on 2020-11-26 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemongo', '0042_auto_20201120_2331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='update',
            name='badge_pokemon_caught_at_your_lures',
            field=models.PositiveIntegerField(blank=True, help_text='Use a Lure Module to help another Trainer catch a Pokémon.', null=True, verbose_name='Picnicker'),
        ),
    ]
