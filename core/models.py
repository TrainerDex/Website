from __future__ import annotations

import logging
import re
from datetime import datetime, timedelta

import requests
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.discord.provider import DiscordAccount
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from pytz import common_timezones

from config.abstract_models import PublicModel

logger = logging.getLogger("django.trainerdex")


def get_guild_info(guild_id: int) -> dict[str, str | int | list | dict | None]:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/guilds/{guild_id}",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


def list_guild_members(
    guild_id: int, limit=1000
) -> list[dict[str, str | list[int] | bool | dict[str, str | bool | int]]]:
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


def get_guild_member(
    guild_id: int, user_id: int
) -> dict[str, str | list[int] | bool | dict[str, str | bool | int]]:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/guilds/{guild_id}/members/{user_id}",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


def get_guild_channels(
    guild_id: int,
) -> list[
    dict[str, str | int | bool | list[dict[str, str | int]] | list[dict[str, str | bool | int]]]
]:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/guilds/{guild_id}/channels",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


def get_channel(
    channel_id: int,
) -> dict[str, str | int | bool | list[dict[str, str | int]] | list[dict[str, str | bool | int]]]:
    base_url = "https://discordapp.com/api/v{version_number}".format(version_number=6)
    r = requests.get(
        f"{base_url}/channels/{channel_id}",
        headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
    )
    r.raise_for_status()
    return r.json()


class DiscordGuild(models.Model):
    id: int = models.BigIntegerField(primary_key=True, verbose_name="ID")
    data: dict | list = models.JSONField(null=True, blank=True)
    cached_date: datetime = models.DateTimeField(auto_now_add=True)
    has_access: bool = models.BooleanField(default=False)
    members: models.QuerySet[DiscordUser] = models.ManyToManyField(
        "DiscordUser",
        through="DiscordGuildMembership",
        through_fields=("guild", "user"),
        related_name="guilds",
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(hours=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def has_data(self) -> bool:
        return bool(self.data)

    has_data.boolean = True
    has_data.short_description = _("got data")

    @property
    def name(self) -> str:
        return self.data.get("name")

    @property
    def normalized_name(self) -> str:
        if self.name:
            return re.sub(r"(?:Pok[eé]mon?\s?(Go)?(GO)?\s?-?\s)", "", self.name)

    @property
    def owner(self) -> int | SocialAccount:
        if self.data.get("owner_id"):
            try:
                return DiscordUser.objects.get(uid=self.data.get("owner_id"))
            except DiscordUser.DoesNotExist:
                pass
        return self.data.get("owner_id")

    def __str__(self) -> str:
        return self.name or f"Discord Guild with ID {self.id}"

    @transaction.atomic
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

    @transaction.atomic
    def sync_members(self) -> str | dict[str, list[str]]:  # Is this a bug?
        try:
            guild_api_members = list_guild_members(self.id)
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
            return {"warning": ["Failed to get server information from Discord"]}
        existing_social_accounts_uids = DiscordUser.objects.values_list("uid", flat=True)
        existing_social_accounts = list(DiscordUser.objects.all())
        existing_discord_memberships = list(
            DiscordGuildMembership.objects.filter(guild=self).prefetch_related("user")
        )
        new_discord_memberships = []
        amended_discord_memberships = []
        for x in guild_api_members:
            if x["user"]["id"] in existing_social_accounts_uids:
                existing_membership = [
                    y for y in existing_discord_memberships if y.user.uid == x["user"]["id"]
                ]
                if existing_membership:
                    e = existing_membership[0]
                    e.data = x
                    e.cached_date = timezone.now()
                    amended_discord_memberships.append(e)
                else:
                    new_discord_memberships.append(
                        DiscordGuildMembership(
                            guild=self,
                            user=[y for y in existing_social_accounts if y.uid == x["user"]["id"]][
                                0
                            ],
                            active=True,
                            data=x,
                            cached_date=timezone.now(),
                        )
                    )
        DiscordGuildMembership.objects.filter(guild=self, active=False).filter(
            user__uid__in=[x["user"]["id"] for x in guild_api_members]
        ).update(active=True)
        DiscordGuildMembership.objects.bulk_update(
            amended_discord_memberships, ["data", "cached_date"]
        )
        DiscordGuildMembership.objects.bulk_create(new_discord_memberships, ignore_conflicts=True)
        DiscordGuildMembership.objects.filter(guild=self, active=True).exclude(
            user__uid__in=[x["user"]["id"] for x in guild_api_members]
        ).update(active=False)

        return _("Succesfully updated {x} of {y} {guild} members").format(
            x=DiscordGuildMembership.objects.filter(guild=self).count(),
            y=len(guild_api_members),
            guild=self,
        )

    @transaction.atomic
    def sync_roles(self) -> None:
        guild_roles = self.data.get("roles")
        roles = [
            DiscordRole(id=int(role["id"]), guild=self, data=role, cached_date=timezone.now())
            for role in guild_roles
        ]
        DiscordRole.objects.bulk_create(roles, ignore_conflicts=True)
        DiscordRole.objects.bulk_update(roles, ["data", "cached_date"])

    @transaction.atomic
    def download_channels(self) -> None:
        try:
            guild_channels = get_guild_channels(self.id)
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get information")
        else:
            channels = [
                DiscordChannel(
                    id=int(channel["id"]),
                    guild=self,
                    data=channel,
                    cached_date=timezone.now(),
                )
                for channel in guild_channels
            ]
            DiscordChannel.objects.bulk_create(channels, ignore_conflicts=True)
            DiscordChannel.objects.bulk_update(channels, ["data", "cached_date"])

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Guild")
        verbose_name_plural = _("Discord Guilds")


class DiscordGuildSettings(DiscordGuild):
    # Localization settings
    language: str = models.CharField(
        default=settings.LANGUAGE_CODE,
        choices=settings.LANGUAGES,
        max_length=len(max(settings.LANGUAGES, key=lambda x: len(x[0]))[0]),
    )
    timezone: str = models.CharField(
        default=settings.TIME_ZONE,
        choices=((x, x) for x in common_timezones),
        max_length=len(max(common_timezones, key=len)),
    )

    # Needed for automatic renaming features
    renamer: bool = models.BooleanField(
        default=True,
        verbose_name=_("Rename users when they join."),
        help_text=_(
            "This setting will rename a user to their Pokémon Go username whenever they join your server and when their name changes on here."
        ),
    )
    renamer_with_level: bool = models.BooleanField(
        default=False,
        verbose_name=_("Rename users with their level indicator"),
        help_text=_(
            "This setting will add a level to the end of their username on your server. "
            "Their name will update whenever they level up."
        ),
    )
    renamer_with_level_format: str = models.CharField(
        default="int",
        verbose_name=_("Level Indicator format"),
        max_length=50,
        choices=[("int", "40"), ("circled_level", "㊵")],
    )

    # Needed for discordbot/management/commands/leaderboard_cron.py
    monthly_gains_channel: DiscordChannel = models.OneToOneField(
        "DiscordChannel",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="monthly_gains_channel",
        limit_choices_to={"data__type": 0},
    )


@receiver(post_save, sender=DiscordGuild)
def new_guild(sender: type[DiscordGuild], **kwargs) -> None:
    if not kwargs["raw"]:
        DiscordGuildSettings.objects.get_or_create(pk=kwargs["instance"].id)
        kwargs["instance"].sync_members()


class DiscordChannel(models.Model):
    id: int = models.BigIntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    guild: DiscordGuild = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
        related_name="channels",
    )
    data: dict | list = models.JSONField(
        null=True,
        blank=True,
    )
    cached_date: datetime = models.DateTimeField(
        auto_now_add=True,
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(days=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def has_data(self) -> bool:
        return bool(self.data)

    has_data.boolean = True
    has_data.short_description = _("got data")

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
    def position(self) -> int | None:
        return self.data.get("position")

    @property
    def name(self) -> str | None:
        return self.data.get("name")

    @property
    def topic(self) -> str | None:
        return self.data.get("topic")

    def _nsfw(self) -> bool | None:
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
    id: int = models.BigIntegerField(
        primary_key=True,
        verbose_name="ID",
    )
    guild: DiscordGuild = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
        related_name="roles",
    )
    data: dict | list = models.JSONField(
        null=True,
        blank=True,
    )
    cached_date: datetime = models.DateTimeField(
        auto_now_add=True,
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(days=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def has_data(self) -> bool:
        return bool(self.data)

    has_data.boolean = True
    has_data.short_description = _("got data")

    def __str__(self) -> str:
        return f"{self.name} in {self.guild}"

    @property
    def name(self) -> str | None:
        return self.data.get("name")

    @property
    def color(self) -> int | None:
        return self.data.get("color")

    def _hoist(self) -> bool | None:
        return self.data.get("hoist")

    _hoist.boolean = True
    hoist = property(_hoist)

    @property
    def position(self) -> int | None:
        return self.data.get("position")

    @property
    def permissions(self) -> int | None:
        return self.data.get("permissions")

    def _managed(self) -> bool | None:
        return self.data.get("managed")

    _managed.short_description = "managed"
    managed = property(_managed)

    def _mentionable(self) -> bool | None:
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
    def get_queryset(self) -> models.QuerySet[DiscordUser]:
        return super(DiscordUserManager, self).get_queryset().filter(provider="discord")

    def create(self, **kwargs) -> DiscordUser:
        kwargs.update({"provider": "discord"})
        return super(DiscordUserManager, self).create(**kwargs)


class DiscordUser(SocialAccount):
    objects = DiscordUserManager()

    def __str__(self) -> str:
        dflt = super(DiscordUser, self).__str__()
        prvdr: DiscordAccount = self.get_provider_account()
        result = prvdr.to_str()
        if result != super(type(prvdr), prvdr).to_str():
            return result
        return dflt

    def has_data(self) -> bool:
        return bool(self.extra_data)

    has_data.boolean = True
    has_data.short_description = _("got data")

    class Meta:
        proxy = True
        verbose_name = _("Discord User")
        verbose_name_plural = _("Discord Users")


class DiscordGuildMembership(models.Model):
    guild: DiscordGuild = models.ForeignKey(
        DiscordGuild,
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    user: DiscordUser = models.ForeignKey(
        DiscordUser,
        on_delete=models.CASCADE,
        related_name="guild_memberships",
    )
    active: bool = models.BooleanField(
        default=True,
    )
    nick_override: str | None = models.CharField(
        null=True,
        blank=True,
        max_length=32,
    )

    data: dict | list = models.JSONField(
        null=True,
        blank=True,
    )
    cached_date: datetime = models.DateTimeField(
        auto_now_add=True,
    )

    def _outdated(self) -> bool:
        return (timezone.now() - self.cached_date) > timedelta(days=1)

    _outdated.boolean = True
    outdated = property(_outdated)

    def has_data(self) -> bool:
        return bool(self.data)

    has_data.boolean = True
    has_data.short_description = _("got data")

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
    def nick(self) -> str | None:
        return self.data.get("nick")

    @property
    def display_name(self) -> str:
        return self.nick or str(self.user)

    @property
    def roles(self) -> models.QuerySet[DiscordRole]:
        if self.data.get("roles"):
            return DiscordRole.objects.filter(id__in=[str(x) for x in self.data.get("roles")])
        else:
            return DiscordRole.objects.none()

    def _deaf(self) -> bool | None:
        return self.data.get("deaf")

    _deaf.boolean = True
    deaf = property(_deaf)

    def _mute(self) -> bool | None:
        return self.data.get("mute")

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


class Service(PublicModel):
    name = models.CharField(verbose_name=_("name"), max_length=32)
    description = models.TextField(verbose_name=_("description"), blank=True)

    def __str__(self):
        return self.name

    def get_status(self) -> ServiceStatus:
        return self.statuses.latest("created_at")


class StatusChoices(models.TextChoices):
    UP = "UP", _("Up")
    DOWN = "DOWN", _("Down")
    UNSTABLE = "UNSTABLE", _("Unstable")
    MAINTENANCE = "MAINTENANCE", _("Scheduled Maintenance")
    UNKNOWN = "UNKNOWN", _("Unknown")


class ServiceStatus(PublicModel):
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        verbose_name=_("service"),
        related_name="statuses",
    )
    status = models.CharField(
        choices=StatusChoices.choices,
        max_length=len(max(StatusChoices.values, key=len)),
        verbose_name=_("status"),
    )
    reason = models.TextField(verbose_name=_("reason"), blank=True)

    def __str__(self):
        return f"{self.service} is {self.status}"
