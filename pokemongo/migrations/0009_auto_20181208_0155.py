# Generated by Django 2.1.3 on 2018-12-08 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_discordguildrole"),
        ("pokemongo", "0008_auto_20181207_1928"),
    ]

    operations = [
        migrations.AddField(
            model_name="communitymembershipdiscord",
            name="exclude_roles",
            field=models.ManyToManyField(
                blank=True,
                related_name="exclude_roles_community_membership_discord",
                to="core.DiscordGuildRole",
            ),
        ),
        migrations.AddField(
            model_name="communitymembershipdiscord",
            name="include_roles",
            field=models.ManyToManyField(
                blank=True,
                related_name="include_roles_community_membership_discord",
                to="core.DiscordGuildRole",
            ),
        ),
        migrations.AlterField(
            model_name="community",
            name="memberships_discord",
            field=models.ManyToManyField(
                blank=True,
                through="pokemongo.CommunityMembershipDiscord",
                to="core.DiscordGuild",
            ),
        ),
        migrations.AlterField(
            model_name="community",
            name="memberships_personal",
            field=models.ManyToManyField(blank=True, to="pokemongo.Trainer"),
        ),
    ]