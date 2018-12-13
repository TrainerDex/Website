import requests

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.postgres import fields as postgres_fields
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.db.models.signals import *
from django.dispatch import receiver
from django.utils.translation import pgettext_lazy, gettext_lazy as _, ngettext
from django.utils import timezone

def get_guild_info(guild_id: int):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/guilds/{guild_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
    r.raise_for_status()
    return r.json()

def get_guild_members(guild_id: int, limit=1000, snowflake=None):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/guilds/{guild_id}/members", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"}, params={'limit': limit, 'snowflake': snowflake})
    r.raise_for_status()
    return r.json()
    
def get_guild_channels(guild_id: int):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/guilds/{guild_id}/channels", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
    r.raise_for_status()
    return r.json()

def get_channel(channel_id: int):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/channels/{channel_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
    r.raise_for_status()
    return r.json()

class DiscordGuild(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        SocialAccount,
        through='DiscordGuildMembership',
        through_fields=('guild', 'user')
    )
    
    settings_pokemongo_rename = models.BooleanField(default=True, help_text=_("""This setting will rename a user to their Pokémon Go username whenever they join your server and when their name changes on here. Pairs great with White Wine, Wensleydale and a Denied "Change Nickname" permission."""))
    settings_pokemongo_rename_with_level = models.BooleanField(default=True, help_text=_("""This setting will add a level to the end of their username on your server. Their name will update whenever they level up. Pairs great with Red Wine, Pears and the above settings."""))
    settings_pokemongo_rename_with_level_format = models.CharField(default='int', max_length=10, choices=(('int', _("Plain ol' Numbers")), ('circled_level', _("Circled Numbers ㊵"))))
    
    def __str__(self):
        try:
            return str(self.data['name'])
        except:
            return f"Discord Guild with ID {self.id}"
    
    def refresh_from_api(self):
        try:
            self.data = get_guild_info(self.id)
            self.cached_date = timezone.now()
            self.sync_roles()
        except:
            print("Failed to get server information from Discord")
        else:
            self.save()
    
    def admin(self):
        """Function to display server admin"""
        try:
            return SocialAccount.objects.get(provider='discord', uid=self.data["owner_id"])
        except SocialAccount.DoesNotExist:
            return self.data["owner_id"]
        except:
            return ''
    
    def sync_members(self):
        try:
            guild_api_members = get_guild_members(self.id)
        except:
            print("Failed to get server information from Discord")
            return {'warning' ["Failed to get server information from Discord"]}
        new_members = [DiscordGuildMembership(
                guild=self,
                user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"]),
                active=True,
                data=x,
                cached_date=timezone.now()
            ) for x in guild_api_members if SocialAccount.objects.filter(provider='discord', uid=x["user"]["id"]).exists() and not DiscordGuildMembership.objects.filter(guild=self,
            user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"])).exists()]
        print(new_members)
        bulk = DiscordGuildMembership.objects.bulk_create(new_members)
        
        reactivate_members = DiscordGuildMembership.objects.filter(guild=self, active=False, user__uid__in=[x["user"]["id"] for x in guild_api_members])
        print(reactivate_members.all())
        reactivate_members.update(active=True)
        
        inactive_members = DiscordGuildMembership.objects.filter(guild=self).exclude(user__uid__in=[x["user"]["id"] for x in guild_api_members])
        print(inactive_members.all())
        inactive_members.update(active=False)
        
        return {'success': [
                    ngettext(
                        "Succesfully imported {success} of {total} ({real_total}) new member to {guild}",
                        "Succesfully imported {success} of {total} ({real_total}) new members to {guild}", len(guild_api_members)
                    ).format(success=len(bulk), total=len(new_members), real_total=len(guild_api_members), guild=self),
                    ngettext(
                        "Succesfully added {count} member back into {guild}",
                        "Succesfully added {count} members back into {guild}", len(guild_api_members)
                    ).format(count=reactivate_members.count(), guild=self)
                ],
                'warning': [
                    ngettext(
                        "{count} member left {guild}",
                        "{count} members left {guild}", inactive_members.count()
                    ).format(count=inactive_members.count(), guild=self)
                ]}
        
    def sync_roles(self):
        try:
            guild_roles = self.data["roles"]
        except:
            print("Failed to get server information from Discord")
            return None
        
        for role in guild_roles:
            x = DiscordGuildRole.objects.get_or_create(id=int(role["id"]), guild=self, defaults={'data': role, 'cached_date': timezone.now()})
        
    def download_channels(self):
        try:
            guild_channels = get_guild_channels(self.id)
        except:
            print("Failed to get information")
            return None
        
        for channel in guild_channels:
            x = DiscordGuildChannel.objects.get_or_create(id=int(channel["id"]), guild=self, defaults={'data': channel, 'cached_date': timezone.now()})
    
    def clean(self):
        self.refresh_from_api()
    
    class Meta:
        verbose_name = _("Discord Guild")
        verbose_name_plural = _("Discord Guilds")

@receiver(post_save, sender=DiscordGuild)
def new_guild(sender, **kwargs):
    if kwargs['created']:
        kwargs['instance'].sync_members()
    return None

class DiscordGuildChannel(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    guild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE)
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.data['name']} in {self.guild}"
    
    def name(self):
        return self.data["name"]
    name.short_description = _('name')
    
    def refresh_from_api(self):
        try:
            self.data = get_channel(self.id)
            self.cached_date = timezone.now()
        except:
            print("Failed to get server information from Discord")
        else:
            self.save()
    
    def clean(self):
        self.refresh_from_api()
    
    class Meta:
        verbose_name = _("Discord Channel")
        verbose_name_plural = _("Discord Channels")

class DiscordGuildRole(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    guild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE)
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.data['name']} in {self.guild}"
    
    def name(self):
        return self.data["name"]
    name.short_description = _('name')

    def position(self):
        return int(self.data["position"])
    position.short_description = _('position')
    
    def refresh_from_api(self):
        try:
            self.data = get_channel(self.id)
            self.cached_date = timezone.now()
        except:
            print("Failed to get server information from Discord")
        else:
            self.save()
    
    def clean(self):
        self.refresh_from_api()
    
    class Meta:
        verbose_name = _("Discord Role")
        verbose_name_plural = _("Discord Roles")
        ordering = ['guild__id', '-data__position']

class DiscordGuildMembership(models.Model):
    guild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE)
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, limit_choices_to={'provider': 'discord'})
    active = models.BooleanField(default=True)
    
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user} in {self.guild}"
    
    def refresh_from_api(self):
        try:
            self.data = get_guild_members(self.guild.id, limit=1, snowflake=self.user.uid)[0]
            self.cached_date = timezone.now()
        except:
            print("Failed to get server information from Discord")
        else:
            self.save()
    
    def clean(self):
        if self.user.provider != 'discord':
            raise ValidationError(_("{} is not of type 'discord'").format(user))
        
        self.refresh_from_api()
    
    class Meta:
        verbose_name = _("Discord Member")
        verbose_name_plural = _("Discord Members")
        unique_together = (("guild", "user"),)
