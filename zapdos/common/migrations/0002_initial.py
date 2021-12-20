# Generated by Django 3.2.10 on 2021-12-11 20:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("pokemongo", "0001_initial"),
        ("common", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="faction_alliances",
            field=models.ManyToManyField(
                related_name="members",
                through="pokemongo.FactionAlliance",
                to="pokemongo.Faction",
                verbose_name="Faction Alliances",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AlterOrderWithRespectTo(
            name="usernamehistory",
            order_with_respect_to="user",
        ),
    ]