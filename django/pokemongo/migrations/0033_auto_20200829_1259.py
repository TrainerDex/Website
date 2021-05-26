import django.core.validators
from django.db import migrations, models


def clear_gen8(apps, schema_editor):
    Update = apps.get_model("pokemongo", "Update")
    Update.objects.update(badge_pokedex_entries_gen8=None)


class Migration(migrations.Migration):

    dependencies = [
        ("pokemongo", "0032_remove_trainer_leaderboard_region"),
    ]

    operations = [
        migrations.RenameField(
            model_name="update",
            old_name="badge_photobombadge_rocket_grunts_defeated",
            new_name="badge_rocket_grunts_defeated",
        ),
        migrations.AlterField(
            model_name="update",
            name="badge_pokedex_entries_gen8",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Register x Pokémon first discovered in the Alola region to the Pokédex.",
                null=True,
                validators=[django.core.validators.MaxValueValidator(2)],
                verbose_name="Galar",
            ),
        ),
        migrations.RunPython(clear_gen8, migrations.RunPython.noop),
    ]
