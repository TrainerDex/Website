import datetime
import logging
import re

import requests
import django.contrib.postgres.fields
from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _, ngettext, pgettext_lazy
from django.utils import timezone
from exclusivebooleanfield.fields import ExclusiveBooleanField
from pytz import common_timezones

from trainerdex.validators import PokemonGoUsernameValidator

log = logging.getLogger('django.trainerdex')


class User(AbstractUser):
    """The model used to represent a user in the database"""
    
    username = django.contrib.postgres.fields.CICharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        verbose_name=pgettext_lazy("nickname__title", "Nickname"),
        )
    is_service_user = models.BooleanField(default=False)


class Nickname(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name=pgettext_lazy("profile__user__title", "User"),
        )
    nickname = django.contrib.postgres.fields.CICharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        db_index=True,
        verbose_name=pgettext_lazy("nickname__title", "Nickname"),
        )
    active = ExclusiveBooleanField(
        on='user',
        )
    
    def __str__(self):
        return self.nickname
        
    class Meta:
        ordering = ['nickname']

@receiver(post_save, sender=User)
def create_nickname(sender, instance, created, **kwargs) -> Nickname:
    if kwargs.get('raw'):
        # End early, one should not query/modify other records in the database as the database might not be in a consistent state yet.
        return None
    
    if instance.is_service_user:
        # End early, service users shouldn't have Trainer objects
        return None
    
    if created:
        return Nickname.objects.create(user=instance, nickname=instance.username, active=True)

@receiver(post_save, sender=Nickname)
def update_username(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        # End early, one should not query/modify other records in the database as the database might not be in a consistent state yet.
        return None
    
    if instance.active:
        instance.user.username = istance.nickname
        instance.user.save(update_fields=['username'])
        # TODO: Generate an email or notice for the user alerting them of this change.


# def get_guild_info(guild_id: int):
#     base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#     r = requests.get(f"{base_url}/guilds/{guild_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
#     try:
#         r.raise_for_status()
#     except:
#         return r.status_code
#     return r.json()
#
# def get_guild_members(guild_id: int, limit=1000):
#     base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#     previous=None
#     more=True
#     result = []
#     while more:
#         r = requests.get(f"{base_url}/guilds/{guild_id}/members", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"}, params={'limit': limit, 'after': previous})
#         r.raise_for_status()
#         more = bool(r.json())
#         if more:
#             result += r.json()
#             previous = result[-1]['user']['id']
#     return result
#
# def get_guild_member(guild_id: int, user_id: int):
#     base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#     r = requests.get(f"{base_url}/guilds/{guild_id}/members/{user_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
#     r.raise_for_status()
#     return r.json()
#
# def get_guild_channels(guild_id: int):
#     base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#     r = requests.get(f"{base_url}/guilds/{guild_id}/channels", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
#     r.raise_for_status()
#     return r.json()
#
# def get_channel(channel_id: int):
#     base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#     r = requests.get(f"{base_url}/channels/{channel_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
#     r.raise_for_status()
#     return r.json()
#
#
# class DiscordGuild(models.Model):
#     id = models.BigIntegerField(
#         primary_key=True,
#         verbose_name="ID",
#         )
#     data = django.contrib.postgres.fields.JSONField(
#         null=True,
#         blank=True,
#         )
#     cached_date = models.DateTimeField(auto_now_add=True)
#     has_access = models.BooleanField(default=False)
#     members = models.ManyToManyField(
#         'DiscordUser',
#         through='DiscordGuildMembership',
#         through_fields=('guild', 'user'),
#         )
#
#     def _outdated(self):
#         return (timezone.now()-self.cached_date) > datetime.timedelta(hours=1)
#     _outdated.boolean = True
#     outdated = property(_outdated)
#
#     def has_data(self):
#         return bool(self.data)
#     has_data.boolean = True
#     has_data.short_description = 'got data'
#
#     @property
#     def name(self):
#         if self.data and 'name' in self.data:
#             return self.data['name']
#
#     @property
#     def normalized_name(self):
#         if self.data and 'name' in self.data:
#             return re.sub(r'(?:Pok[eé]mon?\s?(Go)?(GO)?\s?-?\s)', '', self.data['name'])
#
#     @property
#     def owner(self):
#         if self.data:
#             if 'owner_id' in self.data:
#                 try:
#                     return DiscordUser.objects.get(uid=self.data['owner_id'])
#                 except SocialAccount.DoesNotExist:
#                     pass
#             return self.data['owner_id']
#
#     def __str__(self):
#         try:
#             return str(self.name)
#         except:
#             return f"Discord Guild with ID {self.id}"
#
#     def refresh_from_api(self):
#         logging.info(f"Updating {self}")
#         try:
#             data_or_code = get_guild_info(self.id)
#             if type(data_or_code) == int:
#                 self.has_access = False
#             else:
#                 self.data = data_or_code
#                 self.has_access = True
#                 self.cached_date = timezone.now()
#                 self.sync_roles()
#         except:
#             log.exception("Failed to get server information from Discord")
#         else:
#             self.save()
#
#     def sync_members(self):
#         try:
#             guild_api_members = get_guild_members(self.id)
#         except:
#             log.exception("Failed to get server information from Discord")
#             return {'warning': ["Failed to get server information from Discord"]}
#         new_members = [DiscordGuildMembership(
#                 guild=self,
#                 user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"]),
#                 active=True,
#                 data=x,
#                 cached_date=timezone.now()
#             ) for x in guild_api_members if SocialAccount.objects.filter(provider='discord', uid=x["user"]["id"]).exists() and not DiscordGuildMembership.objects.filter(guild=self,
#             user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"])).exists()]
#         bulk = DiscordGuildMembership.objects.bulk_create(new_members)
#
#         reactivate_members = DiscordGuildMembership.objects.filter(guild=self, active=False, user__uid__in=[x["user"]["id"] for x in guild_api_members])
#         reactivate_members.update(active=True)
#
#         inactive_members = DiscordGuildMembership.objects.filter(guild=self, active=True).exclude(user__uid__in=[x["user"]["id"] for x in guild_api_members])
#         inactive_members.update(active=False)
#
#         return {'success': [
#                     ngettext(
#                         "Succesfully imported {success} of {total} ({real_total}) new member to {guild}",
#                         "Succesfully imported {success} of {total} ({real_total}) new members to {guild}", len(guild_api_members)
#                     ).format(success=len(bulk), total=len(new_members), real_total=len(guild_api_members), guild=self),
#                     ngettext(
#                         "Succesfully added {count} member back into {guild}",
#                         "Succesfully added {count} members back into {guild}", len(guild_api_members)
#                     ).format(count=reactivate_members.count(), guild=self)
#                 ],
#                 'warning': [
#                     ngettext(
#                         "{count} member left {guild}",
#                         "{count} members left {guild}", inactive_members.count()
#                     ).format(count=inactive_members.count(), guild=self)
#                 ]}
#
#     def sync_roles(self):
#         try:
#             guild_roles = self.data["roles"]
#         except:
#             log.exception("Failed to get server information from Discord")
#             return None
#
#         for role in guild_roles:
#             x = DiscordRole.objects.get_or_create(id=int(role["id"]), guild=self, defaults={'data': role, 'cached_date': timezone.now()})
#
#     def download_channels(self):
#         try:
#             guild_channels = get_guild_channels(self.id)
#         except:
#             log.exception("Failed to get information")
#             return None
#
#         for channel in guild_channels:
#             x = DiscordChannel.objects.get_or_create(id=int(channel["id"]), guild=self, defaults={'data': channel, 'cached_date': timezone.now()})
#
#     def clean(self):
#         self.refresh_from_api()
#
#     class Meta:
#         verbose_name = _("Discord Guild")
#         verbose_name_plural = _("Discord Guilds")
#
# class DiscordGuildSettings(DiscordGuild):
#     # Localization settings
#     language = models.CharField(default=settings.LANGUAGE_CODE, choices=settings.LANGUAGES, max_length=len(max(settings.LANGUAGES, key=lambda x: len(x[0]))[0]))
#     timezone = models.CharField(default=settings.TIME_ZONE, choices=((x,x) for x in common_timezones), max_length=len(max(common_timezones, key=len)))
#
#     # Needed for automatic renaming features
#     renamer = models.BooleanField(
#         default=True,
#         verbose_name=_('Rename users when they join.'),
#         help_text=_("This setting will rename a user to their Pokémon Go username whenever they join your server and when their name changes on here."),
#         )
#     renamer_with_level = models.BooleanField(
#         default=False,
#         verbose_name=_('Rename users with their level indicator'),
#         help_text=_("This setting will add a level to the end of their username on your server. Their name will update whenever they level up."),
#         )
#     renamer_with_level_format = models.CharField(
#         default='int',
#         verbose_name=_('Level Indicator format'),
#         max_length=50,
#         choices=[
#             ('int', _("Plain ol' Numbers")),
#             ('circled_level', _("Circled Numbers ㊵")),
#             ],
#         )
#
#     # Needed for discordbot/welcome.py
#     welcomer = models.BooleanField(default=False)
#     welcomer_message_new = models.TextField(blank=True, null=True)
#     welcomer_message_existing = models.TextField(blank=True, null=True)
#     welcomer_channel = models.OneToOneField('DiscordChannel', on_delete=models.SET_NULL, null=True, blank=True, related_name='welcomer_channel', limit_choices_to={'data__type':0})
#
#     # Needed for discordbot/management/commands/leaderboard_cron.py
#     monthly_gains_channel = models.OneToOneField('DiscordChannel', on_delete=models.SET_NULL, null=True, blank=True, related_name='monthly_gains_channel', limit_choices_to={'data__type':0})
#     # monthly_gains_period = 'MONTHLY'
#
# @receiver(post_save, sender=DiscordGuild)
# def new_guild(sender, **kwargs):
#     if kwargs['created']:
#         kwargs['instance'].sync_members()
#     return None
#
# class DiscordChannel(models.Model):
#     id = models.BigIntegerField(
#         primary_key=True,
#         verbose_name="ID",
#         )
#     guild = models.ForeignKey(
#         DiscordGuild,
#         on_delete=models.CASCADE,
#         related_name='channels',
#         )
#     data = django.contrib.postgres.fields.JSONField(
#         null=True,
#         blank=True,
#         )
#     cached_date = models.DateTimeField(
#         auto_now_add=True,
#         )
#
#     def _outdated(self):
#         return (timezone.now()-self.cached_date) > datetime.timedelta(days=1)
#     _outdated.boolean = True
#     outdated = property(_outdated)
#
#     def __str__(self):
#         return self.name
#
#     @property
#     def type(self):
#         if self.data and 'type' in self.data:
#             channel_types = ['Text Channel', 'DM', 'Voice Channel', 'Group DM', 'Category']
#             return channel_types[self.data['type']]
#
#     @property
#     def position(self):
#         if self.data and 'position' in self.data:
#             return self.data['position']
#     @property
#     def name(self):
#         if self.data and 'name' in self.data:
#             return self.data['name']
#     @property
#     def topic(self):
#         if self.data and 'topic' in self.data:
#             return self.data['topic']
#
#     def _nsfw(self):
#         if self.data and 'nsfw' in self.data:
#             return self.data['nsfw']
#     _nsfw.boolean = True
#     nsfw = property(_nsfw)
#
#     @property
#     def recipients(self):
#         if self.data and 'recipients' in self.data:
#             return SocialAccount.objects.filter(provider='discord', uid__in=[x['id'] for x in self.data['recipients']])
#         return SocialAccount.objects.none()
#
#     @property
#     def parent(self):
#         if self.data and 'parent_id' in self.data:
#             try:
#                 return DiscordChannel.objects.get(id=self.data['parent_id'])
#             except DiscordChannel.DoesNotExist:
#                 pass
#         return DiscordChannel.objects.none()
#
#     @property
#     def children(self):
#         return DiscordChannel.objects.filter(data__parent_id=str(self.id))
#
#     def refresh_from_api(self):
#         log.info(f"Updating {self}")
#         try:
#             self.data = get_channel(self.id)
#             self.cached_date = timezone.now()
#         except:
#             log.exception("Failed to get server information from Discord")
#
#     def clean(self):
#         self.refresh_from_api()
#
#     class Meta:
#         verbose_name = _("Discord Channel")
#         verbose_name_plural = _("Discord Channels")
#
# class DiscordRole(models.Model):
#     id = models.BigIntegerField(
#         primary_key=True,
#         verbose_name="ID",
#         )
#     guild = models.ForeignKey(
#         DiscordGuild,
#         on_delete=models.CASCADE,
#         related_name='roles',
#         )
#     data = django.contrib.postgres.fields.JSONField(
#         null=True,
#         blank=True,
#         )
#     cached_date = models.DateTimeField(
#         auto_now_add=True,
#         )
#
#     def _outdated(self):
#         return (timezone.now()-self.cached_date) > datetime.timedelta(days=1)
#     _outdated.boolean = True
#     outdated = property(_outdated)
#
#     def __str__(self):
#         return f"{self.name} in {self.guild}"
#
#     @property
#     def name(self):
#         if self.data and 'name' in self.data:
#             return self.data['name']
#
#     @property
#     def color(self):
#         if self.data and 'color' in self.data:
#             if self.data['color'] != 0:
#                 return self.data['color']
#
#     def _hoist(self):
#         if self.data and 'hoist' in self.data:
#             return self.data['hoist']
#     _hoist.boolean = True
#     hoist = property(_hoist)
#
#     @property
#     def position(self):
#         if self.data and 'position' in self.data:
#             return self.data['position']
#
#     @property
#     def permissions(self):
#         if self.data and 'permissions' in self.data:
#             return self.data['permissions']
#
#     def _managed(self):
#         if self.data and 'managed' in self.data:
#             return self.data['managed']
#     _managed.short_description = 'managed'
#     managed = property(_managed)
#
#     def _mentionable(self):
#         if self.data and 'mentionable' in self.data:
#             return self.data['mentionable']
#     _mentionable.short_description = 'mentionable'
#     mentionable = property(_mentionable)
#
#     def refresh_from_api(self):
#         log.info(f"Updating {self}")
#         try:
#             self.data = get_channel(self.id)
#             self.cached_date = timezone.now()
#         except:
#             log.exception("Failed to get server information from Discord")
#
#     def clean(self):
#         self.refresh_from_api()
#
#     class Meta:
#         verbose_name = _("Discord Role")
#         verbose_name_plural = _("Discord Roles")
#         ordering = ['guild__id', '-data__position']
#
# class DiscordUserManager(models.Manager):
#     def get_queryset(self):
#         return super(DiscordUserManager, self).get_queryset().filter(provider='discord')
#
#     def create(self, **kwargs):
#         kwargs.update({'provider': 'discord'})
#         return super(DiscordUserManager, self).create(**kwargs)
#
# class DiscordUser(SocialAccount):
#     objects = DiscordUserManager()
#
#     def __str__(self):
#         if 'username' in self.extra_data and 'discriminator' in self.extra_data:
#             return f"{self.extra_data['username']}#{self.extra_data['discriminator']}"
#         else:
#             return force_text(self.user)
#
#     class Meta:
#         proxy = True
#         verbose_name = _("Discord User")
#         verbose_name_plural = _("Discord Users")
#
# class DiscordGuildMembership(models.Model):
#     guild = models.ForeignKey(
#         DiscordGuild,
#         on_delete=models.CASCADE,
#         )
#     user = models.ForeignKey(
#         DiscordUser,
#         on_delete=models.CASCADE,
#         )
#     active = models.BooleanField(
#         default=True,
#         )
#     nick_override = models.CharField(
#         null=True,
#         blank=True,
#         max_length=32,
#         )
#
#     data = django.contrib.postgres.fields.JSONField(
#         null=True,
#         blank=True,
#         )
#     cached_date = models.DateTimeField(
#         auto_now_add=True,
#         )
#
#     def _outdated(self):
#         return (timezone.now()-self.cached_date) > datetime.timedelta(days=1)
#     _outdated.boolean = True
#     outdated = property(_outdated)
#
#     def _change_nick(self, nick: str):
#         base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#         if len(nick) > 32:
#             raise ValidationError('nick too long')
#         log.info(f"Renaming {self} to {nick}")
#         r = requests.patch(f"{base_url}/guilds/{self.guild.id}/members/{self.user.uid}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"}, json={'nick': nick})
#         log.info(r.status_code)
#         log.info(r.text)
#         self.refresh_from_api()
#
#
#     @property
#     def nick(self):
#         if self.data and 'nick' in self.data:
#             return self.data['nick']
#
#     @property
#     def display_name(self):
#         if self.data:
#             return self.nick or self.data['user']['username']
#         else:
#             return self.user
#
#     @property
#     def roles(self):
#         if self.data and 'roles' in self.data:
#             return DiscordRole.objects.filter(id__in=[str(x) for x in self.data['roles']])
#         else:
#             return DiscordRole.objects.none()
#
#     def _deaf(self):
#         if self.data and 'deaf' in self.data:
#             return self.data['deaf']
#     _deaf.boolean = True
#     deaf = property(_deaf)
#
#     def _mute(self):
#         if self.data and 'mute' in self.data:
#             return self.data['mute']
#     _mute.boolean = True
#     mute = property(_mute)
#
#     def __str__(self):
#         return f"{self.display_name} in {self.guild}"
#
#     def refresh_from_api(self):
#         log.info(f"Updating {self}")
#         try:
#             self.data = get_guild_member(self.guild.id, self.user.uid)
#             if not self.user.extra_data:
#                 self.user.extra_data = self.data['user']
#                 self.user.save()
#             self.cached_date = timezone.now()
#         except:
#             log.exception("Failed to get server information from Discord")
#
#     def clean(self):
#         if self.user.provider != 'discord':
#             raise ValidationError(_("{} is not of type 'discord'").format(user))
#
#         self.refresh_from_api()
#
#     class Meta:
#         verbose_name = _("Discord Member")
#         verbose_name_plural = _("Discord Members")
#         unique_together = (("guild", "user"),)
