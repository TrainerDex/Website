from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trainer', '0003_auto_20170906_1415'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Discord_Relation',
            new_name='DiscordMember',
        ),
        migrations.RenameModel(
            old_name='Discord_Server',
            new_name='DiscordServer',
        ),
        migrations.RenameModel(
            old_name='Discord_User',
            new_name='DiscordUser',
        ),
		migrations.RenameField(
            model_name='trainer',
            old_name='ekpogo',
            new_name='account',
        ),
    ]