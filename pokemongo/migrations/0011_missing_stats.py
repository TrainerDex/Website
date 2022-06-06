# Generated by Django 4.0.5 on 2022-06-06 19:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemongo', '0010_rename_badges'),
    ]

    operations = [
        migrations.AddField(
            model_name='update',
            name='mini_collection',
            field=models.PositiveIntegerField(blank=True, help_text='Complete Collection Challenges.', null=True, verbose_name='Elite Collector'),
        ),
        migrations.AddField(
            model_name='update',
            name='mvt',
            field=models.PositiveIntegerField(blank=True, help_text='Made the Raid Battle Trainer Achievements screen 200 times.', null=True, verbose_name='Raid Expert'),
        ),
        migrations.AddField(
            model_name='update',
            name='trainers_referred',
            field=models.PositiveIntegerField(blank=True, help_text='Refer 20 Trainers', null=True, verbose_name='Friend Finder'),
        ),
        migrations.AlterField(
            model_name='update',
            name='pokedex_entries_gen7',
            field=models.PositiveIntegerField(blank=True, help_text='Register 50 Pokémon first discovered in the Alola region to the Pokédex.', null=True, validators=[django.core.validators.MaxValueValidator(88)], verbose_name='Alola'),
        ),
        migrations.AlterField(
            model_name='update',
            name='pokedex_entries_gen8',
            field=models.PositiveIntegerField(blank=True, help_text='Register 50 Pokémon first discovered in the Alola region to the Pokédex.', null=True, validators=[django.core.validators.MaxValueValidator(89)], verbose_name='Galar'),
        ),
    ]
