# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger('django.trainerdex')
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
from datetime import timedelta

def get_guild_info(guild_id: int):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/guilds/{guild_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
    r.raise_for_status()
    return r.json()

def get_guild_members(guild_id: int, limit=1000):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    previous=None
    more=True
    result = []
    while more:
        r = requests.get(f"{base_url}/guilds/{guild_id}/members", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"}, params={'limit': limit, 'after': previous})
        r.raise_for_status()
        more = bool(r.json())
        if more:
            result += r.json()
            previous = result[-1]['user']['id']
    return result

def get_guild_member(guild_id: int, user_id: int):
    base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
    r = requests.get(f"{base_url}/guilds/{guild_id}/members/{user_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
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
    
    settings_pokemongo_rename = models.BooleanField(default=True, verbose_name=_('Rename users when they join.'), help_text=_("""This setting will rename a user to their Pokémon Go username whenever they join your server and when their name changes on here. Pairs great with White Wine, Wensleydale and a Denied "Change Nickname" permission."""))
    settings_pokemongo_rename_with_level = models.BooleanField(default=False, verbose_name=_('Rename users with their level indicator'), help_text=_("""This setting will add a level to the end of their username on your server. Their name will update whenever they level up. Pairs great with Red Wine, Pears and the above settings."""))
    settings_pokemongo_rename_with_level_format = models.CharField(default='int', verbose_name=_('Level Indicator format'), max_length=50, choices=(('int', _("Plain ol' Numbers")), ('circled_level', _("Circled Numbers ㊵"))))
    
    def _outdated(self):
        return (timezone.now()-self.cached_date) > timedelta(days=1)
    _outdated.boolean = True
    outdated = property(_outdated)
    
    def has_data(self):
        return bool(self.data)
    has_data.boolean = True
    has_data.short_description = 'got data'

    @property
    def name(self):
        if self.data and 'name' in self.data:
            return self.data['name']

    @property
    def icon(self):
        if self.data and 'icon' in self.data:
            return self.data['icon']

    @property
    def splash(self):
        if self.data and 'splash' in self.data:
            return self.data['splash']

    def _is_owner(self):
        if self.data and 'owner' in self.data:
            return self.data['owner']
    _is_owner.boolean = True
    is_owner = property(_is_owner)

    @property
    def owner_id(self):
        if self.data and 'owner_id' in self.data:
            return self.data['owner_id']

    @property
    def owner(self):
        if self.data and 'owner_id' in self.data:
            try:
                return SocialAccount.objects.get(provider='discord', uid=self.data['owner_id'])
            except SocialAccount.DoesNotExist:
                pass
        return self.owner_id

    @property
    def permissions(self):
        if self.data and 'permissions' in self.data:
            return self.data['permissions']

    @property
    def region(self):
        if self.data and 'region' in self.data:
            return self.data['region']

    @property
    def afk_channel_id(self):
        if self.data and 'afk_channel_id' in self.data:
            return self.data['afk_channel_id']

    @property
    def afk_channel(self):
        if self.data and 'afk_channel_id' in self.data:
            try:
                return DiscordChannel.objects.get(id=self.data['afk_channel_id'])
            except DiscordChannel.DoesNotExist:
                pass
        return self.afk_channel_id

    @property
    def afk_timeout(self):
        if self.data and 'afk_timeout' in self.data:
            return self.data['afk_timeout']

    @property
    def verification_level(self):
        if self.data and 'verification_level' in self.data:
            channel_types = ['NONE', 'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH']
            return channel_types[self.data['verification_level']]

    @property
    def default_message_notifications(self):
        if self.data and 'default_message_notifications' in self.data:
            channel_types = ['ALL_MESSAGES', 'ONLY_MENTIONS']
            return channel_types[self.data['default_message_notifications']]

    @property
    def explicit_content_filter(self):
        if self.data and 'explicit_content_filter' in self.data:
            channel_types = ['DISABLED', 'MEMBERS_WITHOUT_ROLES', 'ALL_MEMBERS']
            return channel_types[self.data['explicit_content_filter']]
    
    # roles is a reverse relation

    @property
    def emojis(self):
        if self.data and 'emojis' in self.data:
            return self.data['emojis']

    @property
    def features(self):
        if self.data and 'features' in self.data:
            return self.data['features']

    @property
    def mfa_level(self):
        if self.data and 'mfa_level' in self.data:
            channel_types = ['NONE', 'ELEVATED']
            return channel_types[self.data['mfa_level']]

    @property
    def system_channel_id(self):
        if self.data and 'system_channel_id' in self.data:
            return self.data['system_channel_id']

    @property
    def system_channel(self):
        if self.data and 'system_channel_id' in self.data:
            try:
                return DiscordChannel.objects.get(id=self.data['system_channel_id'])
            except DiscordChannel.DoesNotExist:
                pass
        return self.afk_channel_id
    
    def __str__(self):
        try:
            return str(self.data['name'])
        except:
            return f"Discord Guild with ID {self.id}"
    
    def refresh_from_api(self):
        logging.info(f"Updating {self}")
        try:
            self.data = get_guild_info(self.id)
            self.cached_date = timezone.now()
            self.sync_roles()
        except:
            logger.exception("Failed to get server information from Discord")
        else:
            self.save()
    
    def sync_members(self):
        try:
            guild_api_members = get_guild_members(self.id)
        except:
            logger.exception("Failed to get server information from Discord")
            return {'warning': ["Failed to get server information from Discord"]}
        new_members = [DiscordGuildMembership(
                guild=self,
                user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"]),
                active=True,
                data=x,
                cached_date=timezone.now()
            ) for x in guild_api_members if SocialAccount.objects.filter(provider='discord', uid=x["user"]["id"]).exists() and not DiscordGuildMembership.objects.filter(guild=self,
            user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"])).exists()]
        bulk = DiscordGuildMembership.objects.bulk_create(new_members)
        
        reactivate_members = DiscordGuildMembership.objects.filter(guild=self, active=False, user__uid__in=[x["user"]["id"] for x in guild_api_members])
        reactivate_members.update(active=True)
        
        inactive_members = DiscordGuildMembership.objects.filter(guild=self, active=True).exclude(user__uid__in=[x["user"]["id"] for x in guild_api_members])
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
            logger.exception("Failed to get server information from Discord")
            return None
        
        for role in guild_roles:
            x = DiscordRole.objects.get_or_create(id=int(role["id"]), guild=self, defaults={'data': role, 'cached_date': timezone.now()})
        
    def download_channels(self):
        try:
            guild_channels = get_guild_channels(self.id)
        except:
            logger.exception("Failed to get information")
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

class DiscordChannel(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    guild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE, related_name='channels')
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)
    
    def _outdated(self):
        return (timezone.now()-self.cached_date) > timedelta(days=1)
    _outdated.boolean = True
    outdated = property(_outdated)
    
    def __str__(self):
        return f"{self.name} in {self.guild}"
    
    @property
    def type(self):
        if self.data and 'type' in self.data:
            channel_types = ['GUILD_TEXT', 'DM', 'GUILD_VOICE', 'GROUP_DM', 'GUILD_CATEGORY']
            return channel_types[self.data['type']]

    @property
    def position(self):
        if self.data and 'position' in self.data:
            return self.data['position']
    @property
    def name(self):
        if self.data and 'name' in self.data:
            return self.data['name']
    @property
    def topic(self):
        if self.data and 'topic' in self.data:
            return self.data['topic']

    def _nsfw(self):
        if self.data and 'nsfw' in self.data:
            return self.data['nsfw']
    _nsfw.boolean = True
    nsfw = property(_nsfw)

    @property
    def bitrate(self):
        if self.data and 'bitrate' in self.data:
            return self.data['bitrate']

    @property
    def user_limit(self):
        if self.data and 'user_limit' in self.data:
            return self.data['user_limit']

    @property
    def rate_limit_per_user(self):
        if self.data and 'rate_limit_per_user' in self.data:
            return self.data['rate_limit_per_user']

    @property
    def recipients(self):
        if self.data and 'recipients' in self.data:
            return SocialAccount.objects.filter(provider='discord', uid__in=[x['id'] for x in self.data['recipients']])
        return SocialAccount.objects.none()

    @property
    def icon(self):
        if self.data and 'icon' in self.data:
            return self.data['icon']

    @property
    def owner(self):
        if self.data and 'owner_id' in self.data:
            try:
                return SocialAccount.objects.get(provider='discord', uid=self.data['owner_id'])
            except SocialAccount.DoesNotExist:
                pass
        return SocialAccount.objects.none()

    @property
    def owner_id(self):
        if self.data and 'owner_id' in self.data:
            return self.data['owner_id']

    @property
    def parent(self):
        if self.data and 'parent_id' in self.data:
            try:
                return DiscordChannel.objects.get(id=self.data['parent_id'])
            except DiscordChannel.DoesNotExist:
                pass
        return DiscordChannel.objects.none()

    @property
    def parent_id(self):
        if self.data and 'parent_id' in self.data:
            return self.data['parent_id']
    
    @property
    def children(self):
        return DiscordChannel.objects.filter(data__parent_id=str(self.id))
    
    def refresh_from_api(self):
        logger.info(f"Updating {self}")
        try:
            self.data = get_channel(self.id)
            self.cached_date = timezone.now()
        except:
            logger.exception("Failed to get server information from Discord")
        else:
            self.save()
    
    def clean(self):
        self.refresh_from_api()
    
    class Meta:
        verbose_name = _("Discord Channel")
        verbose_name_plural = _("Discord Channels")

class DiscordRole(models.Model):
    id = models.BigIntegerField(primary_key=True, verbose_name="ID")
    guild = models.ForeignKey(DiscordGuild, on_delete=models.CASCADE, related_name='roles')
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)
    
    def _outdated(self):
        return (timezone.now()-self.cached_date) > timedelta(days=1)
    _outdated.boolean = True
    outdated = property(_outdated)
    
    def __str__(self):
        return f"{self.name} in {self.guild}"

    @property
    def name(self):
        if self.data and 'name' in self.data:
            return self.data['name']

    @property
    def color(self):
        if self.data and 'color' in self.data:
            if self.data['color'] != 0:
                return self.data['color']

    def _hoist(self):
        if self.data and 'hoist' in self.data:
            return self.data['hoist']
    _hoist.boolean = True
    hoist = property(_hoist)

    @property
    def position(self):
        if self.data and 'position' in self.data:
            return self.data['position']

    @property
    def permissions(self):
        if self.data and 'permissions' in self.data:
            return self.data['permissions']

    def _managed(self):
        if self.data and 'managed' in self.data:
            return self.data['managed']
    _managed.short_description = 'managed'
    managed = property(_managed)

    def _mentionable(self):
        if self.data and 'mentionable' in self.data:
            return self.data['mentionable']
    _mentionable.short_description = 'mentionable'
    mentionable = property(_mentionable)
    
    def refresh_from_api(self):
        logger.info(f"Updating {self}")
        try:
            self.data = get_channel(self.id)
            self.cached_date = timezone.now()
        except:
            logger.exception("Failed to get server information from Discord")
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
    
    def _outdated(self):
        return (timezone.now()-self.cached_date) > timedelta(days=1)
    _outdated.boolean = True
    outdated = property(_outdated)

    @property
    def nick(self):
        if self.data and 'nick' in self.data:
            return self.data['nick']

    @property
    def display_name(self):
        if self.data:
            return self.nick or self.data['user']['username']
        else:
            return self.user
    
    @property
    def roles(self):
        if self.data and 'roles' in self.data:
            return DiscordRole.objects.filter(id__in=[str(x) for x in self.data['roles']])
        else:
            return DiscordRole.objects.none()
    
    def _deaf(self):
        if self.data and 'deaf' in self.data:
            return self.data['deaf']
    _deaf.boolean = True
    deaf = property(_deaf)
    
    def _mute(self):
        if self.data and 'mute' in self.data:
            return self.data['mute']
    _mute.boolean = True
    mute = property(_mute)
    
    def __str__(self):
        return f"{self.display_name} in {self.guild}"
    
    def refresh_from_api(self):
        logger.info(f"Updating {self}")
        try:
            self.data = get_guild_member(self.guild.id, self.user.uid)
            if not self.user.extra_data:
                self.user.extra_data = self.data['user']
            self.cached_date = timezone.now()
        except:
            logger.exception("Failed to get server information from Discord")
        else:
            self.user.save()
            self.save()
    
    def clean(self):
        if self.user.provider != 'discord':
            raise ValidationError(_("{} is not of type 'discord'").format(user))
        
        self.refresh_from_api()
    
    class Meta:
        verbose_name = _("Discord Member")
        verbose_name_plural = _("Discord Members")
        unique_together = (("guild", "user"),)
