# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-07-14 13:59
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0055_auto_20180714_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiscordGuild',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('cached_data', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('cached_date', models.DateTimeField(auto_now=True)),
                ('setting_channels_ocr_enabled', django.contrib.postgres.fields.ArrayField(base_field=models.BigIntegerField(), size=None)),
                ('setting_rename_users', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PrivateLeague',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='UUID')),
                ('language', models.CharField(choices=[('af', 'Afrikaans'), ('ar', 'Arabic'), ('ast', 'Asturian'), ('az', 'Azerbaijani'), ('bg', 'Bulgarian'), ('be', 'Belarusian'), ('bn', 'Bengali'), ('br', 'Breton'), ('bs', 'Bosnian'), ('ca', 'Catalan'), ('cs', 'Czech'), ('cy', 'Welsh'), ('da', 'Danish'), ('de', 'German'), ('dsb', 'Lower Sorbian'), ('el', 'Greek'), ('en', 'English'), ('en-au', 'Australian English'), ('en-gb', 'British English'), ('eo', 'Esperanto'), ('es', 'Spanish'), ('es-ar', 'Argentinian Spanish'), ('es-co', 'Colombian Spanish'), ('es-mx', 'Mexican Spanish'), ('es-ni', 'Nicaraguan Spanish'), ('es-ve', 'Venezuelan Spanish'), ('et', 'Estonian'), ('eu', 'Basque'), ('fa', 'Persian'), ('fi', 'Finnish'), ('fr', 'French'), ('fy', 'Frisian'), ('ga', 'Irish'), ('gd', 'Scottish Gaelic'), ('gl', 'Galician'), ('he', 'Hebrew'), ('hi', 'Hindi'), ('hr', 'Croatian'), ('hsb', 'Upper Sorbian'), ('hu', 'Hungarian'), ('ia', 'Interlingua'), ('id', 'Indonesian'), ('io', 'Ido'), ('is', 'Icelandic'), ('it', 'Italian'), ('ja', 'Japanese'), ('ka', 'Georgian'), ('kk', 'Kazakh'), ('km', 'Khmer'), ('kn', 'Kannada'), ('ko', 'Korean'), ('lb', 'Luxembourgish'), ('lt', 'Lithuanian'), ('lv', 'Latvian'), ('mk', 'Macedonian'), ('ml', 'Malayalam'), ('mn', 'Mongolian'), ('mr', 'Marathi'), ('my', 'Burmese'), ('nb', 'Norwegian Bokmål'), ('ne', 'Nepali'), ('nl', 'Dutch'), ('nn', 'Norwegian Nynorsk'), ('os', 'Ossetic'), ('pa', 'Punjabi'), ('pl', 'Polish'), ('pt', 'Portuguese'), ('pt-br', 'Brazilian Portuguese'), ('ro', 'Romanian'), ('ru', 'Russian'), ('sk', 'Slovak'), ('sl', 'Slovenian'), ('sq', 'Albanian'), ('sr', 'Serbian'), ('sr-latn', 'Serbian Latin'), ('sv', 'Swedish'), ('sw', 'Swahili'), ('ta', 'Tamil'), ('te', 'Telugu'), ('th', 'Thai'), ('tr', 'Turkish'), ('tt', 'Tatar'), ('udm', 'Udmurt'), ('uk', 'Ukrainian'), ('ur', 'Urdu'), ('vi', 'Vietnamese'), ('zh-hans', 'Simplified Chinese'), ('zh-hant', 'Traditional Chinese')], max_length=7)),
                ('short_description', models.CharField(max_length=70)),
                ('description', models.TextField(blank=True, null=True)),
                ('vanity', models.SlugField()),
                ('privacy_public', models.BooleanField(default=False)),
                ('security_ban_sync', models.BooleanField(default=False)),
                ('security_kick_sync', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='PrivateLeagueMembershipDiscord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_import', models.BooleanField(default=True)),
                ('security_ban_sync', models.NullBooleanField()),
                ('security_kick_sync', models.NullBooleanField()),
                ('discord', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.DiscordGuild')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.PrivateLeague')),
            ],
        ),
        migrations.CreateModel(
            name='PrivateLeagueMembershipPersonal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary', models.BooleanField(default=True)),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.PrivateLeague')),
                ('trainer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='trainer.Trainer')),
            ],
        ),
        migrations.AddField(
            model_name='privateleague',
            name='memberships_discord',
            field=models.ManyToManyField(through='trainer.PrivateLeagueMembershipDiscord', to='trainer.DiscordGuild'),
        ),
        migrations.AddField(
            model_name='privateleague',
            name='memberships_personal',
            field=models.ManyToManyField(through='trainer.PrivateLeagueMembershipPersonal', to='trainer.Trainer'),
        ),
    ]
