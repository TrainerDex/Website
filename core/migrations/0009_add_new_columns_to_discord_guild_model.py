# Generated by Django 4.1 on 2022-09-20 19:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_prefill_extra_fields"),
    ]

    operations = [
        migrations.RenameField(
            model_name="discordguild",
            old_name="monthly_gains_channel",
            new_name="leaderboard_channel",
        ),
        migrations.RenameField(
            model_name="discordguild",
            old_name="renamer",
            new_name="set_nickname_on_update",
        ),
        migrations.RenameField(
            model_name="discordguild",
            old_name="renamer_with_level_format",
            new_name="level_format",
        ),
        migrations.RemoveField(
            model_name="discordguild",
            name="renamer_with_level",
        ),
        migrations.AddField(
            model_name="discordguild",
            name="assign_roles_on_join",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="instinct_role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.discordrole",
            ),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="mod_role_ids",
            field=models.ManyToManyField(blank=True, db_constraint=False, related_name="+", to="core.discordrole"),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="mystic_role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.discordrole",
            ),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="roles_to_append_on_approval",
            field=models.ManyToManyField(blank=True, db_constraint=False, related_name="+", to="core.discordrole"),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="roles_to_remove_on_approval",
            field=models.ManyToManyField(blank=True, db_constraint=False, related_name="+", to="core.discordrole"),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="set_nickname_on_join",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="tl40_role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.discordrole",
            ),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="tl50_role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.discordrole",
            ),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="valor_role",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.discordrole",
            ),
        ),
        migrations.AddField(
            model_name="discordguild",
            name="weekly_leaderboards_enabled",
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name="discordguild",
            name="leaderboard_channel",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                limit_choices_to={"data__type": 0},
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="core.discordchannel",
            ),
        ),
        migrations.AlterField(
            model_name="discordguild",
            name="level_format",
            field=models.CharField(
                choices=[("none", "None"), ("int", "40"), ("circled_level", "㊵")],
                default="int",
                max_length=50,
                verbose_name="Level Indicator format",
            ),
        ),
        migrations.AlterField(
            model_name="discordguild",
            name="set_nickname_on_update",
            field=models.BooleanField(default=True),
        ),
    ]
