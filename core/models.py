import logging
import requests
import re
from typing import Dict, List, Union, Optional

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.contrib.postgres import fields as postgres_fields
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.encoding import force_text
from django.utils.translation import gettext_lazy as _, ngettext
from django.utils import timezone

from datetime import timedelta
from pytz import common_timezones

logger = logging.getLogger("django.trainerdex")


def get_guild_info(guild_id: int) -> Dict:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/guilds/{guild_id}",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


def get_guild_members(guild_id: int, limit=1000) -> List[Dict]:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    previous = None
    more = True
    result = []
    while more:
        r = requests.get(
            f"{base_url}/guilds/{guild_id}/members",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
            params={"limit": limit, "after": previous},
        )
        r.raise_for_status()
        more = bool(r.json())
        if more:
            result += r.json()
            previous = result[-1]["user"]["id"]
    return result


def get_guild_member(guild_id: int, user_id: int) -> Dict:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/guilds/{guild_id}/members/{user_id}",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


def get_guild_channels(guild_id: int) -> List[Dict]:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/guilds/{guild_id}/channels",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


def get_channel(channel_id: int) -> Dict:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/channels/{channel_id}",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


class DiscordGuild(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    data = postgres_fields.JSONField(null=True, blank=True)
    cached_date = models.DateTimeField(auto_now_add=True)
    has_access = models.BooleanField(default=False)
    members = models.ManyToManyField(
        "DiscordUser",
        through="DiscordGuildMembership",
        through_fields=("guild", "user"),
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(hours=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def has_data(self) -> bool:
        return bool(self.data)

    has_data.boolean = True
    has_data.short_description = "got data"

    @property
    def name(self) -> str:
        return self.data.get("name")

    @property
    def normalized_name(self) -> str:
        if self.name:
            return re.sub(r"(?:Pok[eé]mon?\s?(Go)?(GO)?\s?-?\s)", "", self.name)

    @property
    def owner(self) -> Union[int, SocialAccount]:
        if self.data.get("owner_id"):
            try:
                return DiscordUser.objects.get(uid=self.data.get("owner_id"))
            except DiscordUser.DoesNotExist:
                pass
        return self.data.get("owner_id")

    def __str__(self) -> str:
        return self.name or f"Discord Guild with ID {self.id}"

    def refresh_from_api(self) -> None:
        logging.info(f"Updating {self}")
        try:
            data = get_guild_info(self.id)
            self.data = data
            self.has_access = True
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            self.has_access = False
            logger.exception("Failed to get server information from Discord")
        else:
            self.sync_roles()
        finally:
            self.save()

    def sync_members(self) -> Dict[str, List[str]]:
        try:
            guild_api_members = get_guild_members(self.id)
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
            return {"warning": ["Failed to get server information from Discord"]}
        added_people = []
        amended_people = []
        for x in guild_api_members:
            if SocialAccount.objects.filter(provider="discord", uid=x["user"]["id"]).exists():
                x, y = DiscordGuildMembership.objects.update_or_create(
                    guild=self,
                    user=SocialAccount.objects.get(provider="discord", uid=x["user"]["id"]),
                    defaults={"active": True, "data": x, "cached_date": timezone.now()},
                )
                if y:
                    added_people.append(x)
                else:
                    amended_people.append(x)

        inactive_members = DiscordGuildMembership.objects.filter(guild=self, active=True).exclude(
            user__uid__in=[x["user"]["id"] for x in guild_api_members]
        )
        inactive_members.update(active=False)

        return {
            "success": [
                ngettext(
                    "Succesfully imported {success} of {total} new member to {guild}",
                    "Succesfully imported {success} of {total} new members to {guild}",
                    len(guild_api_members),
                ).format(
                    success=len(added_people) + len(amended_people),
                    total=len(guild_api_members),
                    guild=self,
                )
            ],
            "warning": [
                ngettext(
                    "{count} member left {guild}",
                    "{count} members left {guild}",
                    inactive_members.count(),
                ).format(count=inactive_members.count(), guild=self)
            ],
        }

    def sync_roles(self) -> None:
        guild_roles = self.data.get("roles")
        for role in guild_roles:
            DiscordRole.objects.get_or_create(
                id=int(role["id"]),
                guild=self,
                defaults={"data": role, "cached_date": timezone.now()},
            )

    def download_channels(self) -> None:
        try:
            guild_channels = get_guild_channels(self.id)
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get information")
        else:
            for channel in guild_channels:
                DiscordChannel.objects.get_or_create(
                    id=int(channel["id"]),
                    guild=self,
                    defaults={"data": channel, "cached_date": timezone.now()},
                )

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Guild")
        verbose_name_plural = _("Discord Guilds")


class DiscordGuildSettings(DiscordGuild):
    # Localization settings
    language = models.CharField(
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES,
        max_length=len(max(settings.LANGUAGES, key=lambda x: len(x[0]))[0]),
    )
    timezone = models.CharField(
        default=settings.TIME_ZONE,
        choices=((x, x) for x in common_timezones),
        max_length=len(max(common_timezones, key=len)),
    )

    # Needed for automatic renaming features
    renamer = models.BooleanField(
        default=True,
        verbose_name=_("Rename users when they join."),
        help_text=_(
            "This setting will rename a user to their Pokémon Go username whenever they join your server and when their name changes on here."
        ),
    )
    renamer_with_level = models.BooleanField(
        default=False,
        verbose_name=_("Rename users with their level indicator"),
        help_text=_(
            "This setting will add a level to the end of their username on your server. "
            "Their name will update whenever they level up."
        ),
    )
    renamer_with_level_format = models.CharField(
        default="int",
        verbose_name=_("Level Indicator format"),
        max_length=50,
        choices=[
            ("int", _("Plain ol' Numbers")),
            ("circled_level", _("Circled Numbers ㊵")),
        ],
    )

    # Needed for discordbot/management/commands/leaderboard_cron.py
    monthly_gains_channel = models.OneToOneField(
        "DiscordChannel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monthly_gains_channel",
        limit_choices_to={"data__type": 0},
    )


@receiver(post_save, sender=DiscordGuild)
def new_guild(sender, **kwargs) -> None:
    if kwargs["created"]:
        DiscordGuildSettings.objects.get_or_create(pk=kwargs["instance"].id)
        kwargs["instance"].sync_members()


class DiscordChannel(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    guild = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
        related_name="channels",
    )
    data = postgres_fields.JSONField(
        null=True,
        blank=True,
    )
    cached_date = models.DateTimeField(
        auto_now_add=True,
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(days=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def __str__(self) -> str:
        return self.name

    @property
    def type(self) -> str:
        channel_types = {
            0: "GUILD_TEXT",
            1: "DM",
            2: "GUILD_VOICE",
            3: "GROUP_DM",
            4: "GUILD_CATEGORY",
            5: "GUILD_NEWS",
            6: "GUILD_STORE",
        }
        return channel_types.get(self.data.get("type"), "UNKNOWN")

    @property
    def position(self) -> Optional[int]:
        return self.data.get("position")

    @property
    def name(self) -> Optional[str]:
        return self.data.get("name")

    @property
    def topic(self) -> Optional[str]:
        return self.data.get("topic")

    def _nsfw(self) -> Optional[bool]:
        return self.data.get("nsfw")

    _nsfw.boolean = True
    nsfw = property(_nsfw)

    def refresh_from_api(self) -> None:
        logger.info(f"Updating {self}")
        try:
            self.data = get_channel(self.id)
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Channel")
        verbose_name_plural = _("Discord Channels")


class DiscordRole(models.Model):
    id = models.BigIntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    guild = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
        related_name="roles",
    )
    data = postgres_fields.JSONField(
        null=True,
        blank=True,
    )
    cached_date = models.DateTimeField(
        auto_now_add=True,
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(days=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def __str__(self) -> str:
        return f"{self.name} in {self.guild}"

    @property
    def name(self) -> str:
        return self.data.get("name")

    @property
    def color(self) -> int:
        return self.data.get("color")

    def _hoist(self) -> bool:
        return self.data.get("hoist")

    _hoist.boolean = True
    hoist = property(_hoist)

    @property
    def position(self) -> int:
        return self.data.get("position")

    @property
    def permissions(self) -> int:
        return self.data.get("permissions")

    def _managed(self) -> bool:
        return self.data.get("managed")

    _managed.short_description = "managed"
    managed = property(_managed)

    def _mentionable(self) -> bool:
        return self.data.get("mentionable")

    _mentionable.short_description = "mentionable"
    mentionable = property(_mentionable)

    def refresh_from_api(self) -> None:
        logger.info(f"Updating {self}")
        try:
            self.data = get_channel(self.id)
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Role")
        verbose_name_plural = _("Discord Roles")
        ordering = ["guild__id", "-data__position"]


class DiscordUserManager(models.Manager):
    def get_queryset(self):
        return super(DiscordUserManager, self).get_queryset().filter(provider="discord")

    def create(self, **kwargs):
        kwargs.update({"provider": "discord"})
        return super(DiscordUserManager, self).create(**kwargs)


class DiscordUser(SocialAccount):
    objects = DiscordUserManager()

    def __str__(self) -> str:
        if "username" in self.extra_data and "discriminator" in self.extra_data:
            return f"{self.extra_data['username']}#{self.extra_data['discriminator']}"
        else:
            return force_text(self.user)

    class Meta:
        proxy = True
        verbose_name = _("Discord User")
        verbose_name_plural = _("Discord Users")


class DiscordGuildMembership(models.Model):
    guild = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        DiscordUser,
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(
        default=True,
    )
    nick_override = models.CharField(
        null=True,
        blank=True,
        max_length=32,
    )

    data = postgres_fields.JSONField(
        null=True,
        blank=True,
    )
    cached_date = models.DateTimeField(
        auto_now_add=True,
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(days=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def _change_nick(self, nick: str) -> None:
        base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
        if len(nick) > 32:
            raise ValidationError("nick too long")
        logger.info(f"Renaming {self} to {nick}")
        r = requests.patch(
            f"{base_url}/guilds/{self.guild.id}/members/{self.user.uid}",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
            json={"nick": nick},
        )
        logger.info(r.status_code)
        logger.info(r.text)
        self.refresh_from_api()

    @property
    def nick(self) -> Optional[str]:
        return self.data.get("nick")

    @property
    def display_name(self) -> str:
        return self.nick or str(self.user)

    @property
    def roles(self) -> List[DiscordRole]:
        if self.data.get("roles"):
            return DiscordRole.objects.filter(id__in=[str(x) for x in self.data.get("roles")])
        else:
            return DiscordRole.objects.none()

    def _deaf(self) -> bool:
        if self.data.get("deaf"):
            return self.data["deaf"]

    _deaf.boolean = True
    deaf = property(_deaf)

    def _mute(self) -> bool:
        if self.data.get("mute"):
            return self.data["mute"]

    _mute.boolean = True
    mute = property(_mute)

    def __str__(self) -> str:
        return f"{self.display_name} in {self.guild}"

    def refresh_from_api(self) -> None:
        logger.info(f"Updating {self}")
        try:
            self.data = get_guild_member(self.guild.id, self.user.uid)
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
        else:
            if not self.user.extra_data:
                self.user.extra_data = self.data["user"]
                self.user.save()
            self.cached_date = timezone.now()

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Member")
        verbose_name_plural = _("Discord Members")
        unique_together = (("guild", "user"),)
