# Generated by Django 2.1 on 2018-08-20 14:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0075_auto_20180819_1400'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='factionleader',
            options={'verbose_name': 'Team Leader', 'verbose_name_plural': 'Team Leaders'},
        ),
        migrations.AlterField(
            model_name='update',
            name='xp',
            field=models.PositiveIntegerField(blank=True, help_text='Your Total XP can be found at the bottom of your Pokémon Go profile', null=True, verbose_name='Total XP'),
        ),
    ]