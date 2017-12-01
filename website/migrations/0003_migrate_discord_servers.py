# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from datetime import date

def migrate_discord_servers(apps, schema_editor):
    OldServer = apps.get_model('trainer', 'DiscordServer')
    NewServer = apps.get_model('website', 'Discord')
    for server in OldServer.objects.all():
        extra_data = {}
        extra_data['region'] = server.region
        extra_data['id'] = server.id
            
        NewServer.objects.create(name=server.name, uri='', identifier=server.id, extra_data=extra_data)

class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_auto_20171201_2117'),
        ('trainer', '0008_clear_default_start_dates'),
    ]
    
    operations=[
        migrations.RunPython(migrate_discord_servers),
    ]