# import datetime
import logging

# import requests
import django.contrib.postgres.fields
# from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.auth.models import AbstractUser
# from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _, ngettext, npgettext_lazy
# from django.utils import timezone
from exclusivebooleanfield.fields import ExclusiveBooleanField
# from pytz import common_timezones

from trainerdex.validators import PokemonGoUsernameValidator

log = logging.getLogger('django.trainerdex')


class User(AbstractUser):
    """The model used to represent a user in the database"""
    
    username = django.contrib.postgres.fields.CICharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        error_messages={'unique': _("A user with that username already exists.")},
    )
    gdpr = models.BooleanField(default=True)


class Nickname(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=User._meta.verbose_name,
    )
    nickname = django.contrib.postgres.fields.CICharField(
        max_length=15,
        unique=True,
        validators=[PokemonGoUsernameValidator],
        db_index=True,
        verbose_name=npgettext_lazy("nickname__title", "nickname", "nicknames", 1),
    )
    active = ExclusiveBooleanField(
        on='user',
    )
    
    def __str__(self):
        return self.nickname
        
    class Meta:
        ordering = ['nickname']
        verbose_name = npgettext_lazy("nickname__title", "nickname", "nicknames", 1)
        verbose_name_plural = npgettext_lazy("nickname__title", "nickname", "nicknames", 2)

@receiver(post_save, sender=User)
def create_nickname(sender, instance, created, **kwargs) -> Nickname:
    if kwargs.get('raw'):
        return None
    
    if created:
        return Nickname.objects.create(user=instance, nickname=instance.username, active=True)

@receiver(post_save, sender=Nickname)
def update_username(sender, instance, created, **kwargs):
    if kwargs.get('raw'):
        return None
    
    if instance.active and instance.user.username != instance.nickname:
        instance.user.username = instance.nickname
        instance.user.save(update_fields=['username'])
        # TODO: Generate an email or notice for the user alerting them of this change.


# def get_guild_info(guild_id: int):
#     base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#     r = requests.get(f"{base_url}/guilds/{guild_id}", headers={'Authorization': f"Bot {settings.DISCORD_TOKEN}"})
#     try:
#         r.raise_for_status()
#     except requests.exceptions.HTTPError:
#         return r.status_code
#     return r.json()
#
# def get_guild_members(guild_id: int, limit=1000):
#     base_url = 'https://discordapp.com/api/v{version_number}'.format(version_number=6)
#     previous = None
#     more = True
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
#     )
#     data = django.contrib.postgres.fields.JSONField(
#         null=True,
#         blank=True,
#     )
#     cached_date = models.DateTimeField(auto_now_add=True)
#     has_access = models.BooleanField(default=False)
#     members = models.ManyToManyField(
#         'DiscordUser',
#         through='DiscordGuildMembership',
#         through_fields=('guild', 'user'),
#     )
#
#     def _outdated(self):
#         return (timezone.now()-self.cached_date) > datetime.timedelta(hours=1)
#     _outdated.boolean = True
#     outdated = property(_outdated)
#
#     def has_data(self):
#         return bool(self.data)
#     has_data.boolean = True
#     has_data.short_description = _('got data')
#
#     @property
#     def name(self):
#         return self.data.get('name')
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
#         except requests.exceptions.HTTPError:
#             return f"Discord Guild with ID {self.id}"
#
#     def refresh_from_api(self):
#         logging.info(f"Updating {self}")
#         try:
#             data_or_code = get_guild_info(self.id)
#         except requests.exceptions.HTTPError:
#             log.exception("Failed to get server information from Discord")
#         else:
#             if type(data_or_code) == int:
#                 self.has_access = False
#             else:
#                 self.data = data_or_code
#                 self.has_access = True
#                 self.cached_date = timezone.now()
#                 self.sync_roles()
#             self.save()
#
#     def sync_members(self):
#         try:
#             guild_api_members = get_guild_members(self.id)
#         except requests.exceptions.HTTPError:
#             log.exception("Failed to get server information from Discord")
#             return {'warning': ["Failed to get server information from Discord"]}
#
#         # Replace with a update_or_create() loop
#
#         new_members = [DiscordGuildMembership(
#                 guild=self,
#                 user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"]),
#                 active=True,
#                 data=x,
#                 cached_date=timezone.now(),
#                 ) for x in guild_api_members if SocialAccount.objects.filter(provider='discord', uid=x["user"]["id"]).exists() and not DiscordGuildMembership.objects.filter(
#                     guild=self,
#                     user=SocialAccount.objects.get(provider='discord', uid=x["user"]["id"]),
#                 ).exists()]
#
#
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
#                         "Succesfully imported {success} of {total} ({real_total}) new members to {guild}", len(new_members)
#                         ).format(success=len(bulk), total=len(new_members), real_total=len(guild_api_members), guild=self),
#                     ngettext(
#                         "Succesfully added {count} member back into {guild}",
#                         "Succesfully added {count} members back into {guild}", len(guild_api_members)
#                         ).format(count=reactivate_members.count(), guild=self)
#                 ],
#                 'warning': [
#                     ngettext(
#                         "{count} member left {guild}",
#                         "{count} members left {guild}", inactive_members.count()
#                         ).format(count=inactive_members.count(), guild=self)
#                 ]}
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
#     timezone = models.CharField(default=settings.TIME_ZONE, choices=((x, x) for x in common_timezones), max_length=len(max(common_timezones, key=len)))
#
#     # Needed for automatic renaming features
#     rename_users_on_join = models.BooleanField(
#         default=True,
#         verbose_name=_('Rename users when they join.'),
#         help_text=_("This setting will rename a user to their Pokémon Go username whenever they join your server and when their name changes on here."),
#     )
#     rename_users_on_update = models.BooleanField(
#         default=True,
#         verbose_name=_('Rename users when they update.'),
#         help_text=_("This setting will rename a user to their Pokémon Go username whenever they update their stats."),
#     )
#     renamer_with_level_format = models.CharField(
#         default='false',
#         verbose_name=_('Add levels to a users name'),
#         max_length=50,
#         choices=[
#             ('false' 'None'),
#             ('int', _("Plain ol' Numbers")),
#             ('circled_level', _("Circled Numbers ㊵")),
#             ],
#     )
#
#
# class DiscordChannel(models.Model):
#     pass
#
#
# class DiscordRole(models.Model):
#     pass
#
#
# class DiscordUserManager(models.Manager):
#     def get_queryset(self):
#         return super(DiscordUserManager, self).get_queryset().filter(provider='discord')
#
#     def create(self, **kwargs):
#         kwargs.update({'provider': 'discord'})
#         return super(DiscordUserManager, self).create(**kwargs)
#
#
# class DiscordUser(SocialAccount):
#     objects = DiscordUserManager()
#
#     @property
#     def username(self):
#         return self.extra_data.get('username')
#
#     @property
#     def discriminator(self):
#         return self.extra_data.get('discriminator')
#
#     def __str__(self):
#         if self.username and self.discriminator:
#             return f"{self.username}#{self.discriminator}"
#         else:
#             return str(self.user)
#
#     class Meta:
#         proxy = True
#         verbose_name = _("Discord User")
#         verbose_name_plural = _("Discord Users")
#
#
# class DiscordGuildMembership(models.Model):
#     guild = models.ForeignKey(
#         DiscordGuild,
#         on_delete=models.CASCADE,
#     )
#     user = models.ForeignKey(
#         DiscordUser,
#         on_delete=models.CASCADE,
#     )
#     active = models.BooleanField(
#         default=True,
#     )
#     nick_override = models.CharField(
#         null=True,
#         blank=True,
#         max_length=32,
#     )
#
#     data = django.contrib.postgres.fields.JSONField(
#         null=True,
#         blank=True,
#     )
#     cached_date = models.DateTimeField(
#         null=True,
#         blank=True,
#     )
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
#         return self.data.get('nick')
#
#     @property
#     def display_name(self):
#         if self.nick:
#             return self.nick
#         else:
#             return self.user
#
#     @property
#     def roles(self):
#         pass
#
#     def _deaf(self):
#         return self.data.get('deaf')
#     _deaf.boolean = True
#     deaf = property(_deaf)
#
#     def _mute(self):
#         return self.data.get('mute')
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
#         except requests.exceptions.HTTPError:
#             log.exception("Failed to get server information from Discord")
#
#     def clean(self):
#         if self.user.provider != 'discord':
#             raise ValidationError(_("{} is not of type 'discord'").format(self.user))
#
#         self.refresh_from_api()
#
#     class Meta:
#         verbose_name = _("Discord Member")
#         verbose_name_plural = _("Discord Members")
#         unique_together = (("guild", "user"),)
