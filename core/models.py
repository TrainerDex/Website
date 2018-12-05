import requests

from django.conf import settings
from django.contrib.postgres import fields as postgres_fields
from django.db import models
from django.utils.translation import pgettext_lazy, gettext_lazy as _
from django.utils import timezone

def get_guild_info(guild_id: int):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/guilds/{guild_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
    r.raise_for_status()
    return r.json()
    
def get_guild_members(guild_id: int):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/guilds/{guild_id}/members", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"}, params={'limit': 1000})
    r.raise_for_status()
    return r.json()

class DiscordGuild(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        try:
            return str(self.data['name'])
        except:
            return f"Discord Guild with ID {self.id}"
        
    def clean(self):
        try:
            self.data = get_guild_info(self.id)
            self.cached_date = timezone.now()
        except:
            print("Failed to get server information from Discord")
        else:
            self.save()
        

    class Meta:
        verbose_name = _("Discord Guild")
        verbose_name_plural = _("Discord Guilds")
