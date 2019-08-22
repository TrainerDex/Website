# Generated by Django 2.1.10 on 2019-08-22 22:14

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemongo', '0027_auto_20190520_1453'),
    ]

    operations = [
        migrations.AddField(
            model_name='update',
            name='badge_pokemon_purified',
            field=models.PositiveIntegerField(blank=True, help_text='Purify 500 Shadow Pokémon.', null=True, verbose_name='Purifier'),
        ),
        migrations.AddField(
            model_name='update',
            name='badge_rocket_grunts_defeated',
            field=models.PositiveIntegerField(blank=True, help_text='Defeat 1000 Team GO Rocket Grunts.', null=True, verbose_name='Hero'),
        ),
        migrations.AlterField(
            model_name='update',
            name='badge_pokedex_entries_gen3',
            field=models.PositiveIntegerField(blank=True, help_text='Register 90 Pokémon first discovered in the Hoenn region to the Pokédex.', null=True, validators=[django.core.validators.MaxValueValidator(134)], verbose_name='Hoenn'),
        ),
    ]
