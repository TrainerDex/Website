# Generated by Django 2.1.3 on 2018-12-05 21:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20181205_2102'),
        ('pokemongo', '0004_community'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityMembershipDiscord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_import', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Community Discord Connection',
                'verbose_name_plural': 'Community Discord Connections',
            },
        ),
        migrations.AlterModelOptions(
            name='community',
            options={'verbose_name': 'Community', 'verbose_name_plural': 'Communities'},
        ),
        migrations.AddField(
            model_name='communitymembershipdiscord',
            name='community',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pokemongo.Community'),
        ),
        migrations.AddField(
            model_name='communitymembershipdiscord',
            name='discord',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.DiscordGuild'),
        ),
        migrations.AddField(
            model_name='community',
            name='memberships_discord',
            field=models.ManyToManyField(through='pokemongo.CommunityMembershipDiscord', to='core.DiscordGuild'),
        ),
    ]