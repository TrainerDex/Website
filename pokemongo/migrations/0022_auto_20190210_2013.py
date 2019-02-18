# Generated by Django 2.1.4 on 2019-02-10 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pokemongo', '0021_auto_20190210_1954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='trainer',
            name='faction',
            field=models.SmallIntegerField(choices=[(0, 'No Team'), (1, 'Team Mystic'), (2, 'Team Valor'), (3, 'Team Instinct')], null=True, verbose_name='Team'),
        ),
        migrations.DeleteModel(
            name='Faction',
        ),
    ]