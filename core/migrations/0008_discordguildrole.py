# Generated by Django 2.1.3 on 2018-12-08 01:55

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_discordguildchannel"),
    ]

    operations = [
        migrations.CreateModel(
            name="DiscordGuildRole",
            fields=[
                (
                    "id",
                    models.BigIntegerField(
                        primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "data",
                    django.contrib.postgres.fields.jsonb.JSONField(
                        blank=True, null=True
                    ),
                ),
                ("cached_date", models.DateTimeField(auto_now_add=True)),
                (
                    "guild",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.DiscordGuild",
                    ),
                ),
            ],
            options={
                "verbose_name": "Discord Role",
                "verbose_name_plural": "Discord Roles",
                "ordering": ["guild__id", "-data__position"],
            },
        ),
    ]