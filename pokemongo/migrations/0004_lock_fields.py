# Generated by Django 3.2.12 on 2022-03-17 22:13

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("pokemongo", "0003_populate_new_fields"),
    ]

    operations = [
        migrations.AlterField(
            model_name="trainer",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, verbose_name="Created at"),
        ),
        migrations.AlterField(
            model_name="trainer",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Updated at"),
        ),
        migrations.AlterField(
            model_name="trainer",
            name="uuid",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="UUID"),
        ),
        migrations.AlterField(
            model_name="update",
            name="updated_at",
            field=models.DateTimeField(auto_now=True, verbose_name="Updated at"),
        ),
    ]
