from __future__ import annotations

import logging
from datetime import datetime, timedelta
import time
from typing import List

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

logger = logging.getLogger("django.trainerdex")

DISCORD_BASE_URL = "https://discord.com/api/v10"


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
        related_name=None,
        limit_choices_to={"data__type": 0},
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

    def __str__(self) -> str:
        return self.name or f"Discord Guild with ID {self.id}"

    @transaction.atomic
    def refresh_from_api(self) -> None:
        logging.info(f"Updating {self}")
        try:
            data = self._fetch_one()
            self.data = data
            self.has_access = True
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            self.has_access = False
            logger.exception("Failed to get server information from Discord")
        else:
            self.save(update_fields=("data", "has_access", "cached_date"))
            self.sync_roles()

    def _fetch_one(self):
        r = requests.get(
            f"{DISCORD_BASE_URL}/guilds/{self.id}",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
        )
        r.raise_for_status()
        return r.json()

    @transaction.atomic
    def sync_members(self) -> str | dict[str, list[str]]:  # Is this a bug?
        try:
            guild_api_members = self._fetch_guild_members()
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

    def _fetch_guild_members(self):
        previous = None
        result = []
        while True:
            r = requests.get(
                f"{DISCORD_BASE_URL}/guilds/{self.id}/members",
                headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
                params={"limit": 1000, "after": previous},
            )
            if r.status_code == 429:
                time.sleep(
                    float(r.headers.get("Retry-After", r.headers["X-RateLimit-Reset-After"]))
                )
                continue
            r.raise_for_status()
            data = r.json()
            if data:
                result += r.json()
                previous = result[-1]["user"]["id"]
            else:
                break
        return result

    @transaction.atomic
    def sync_roles(self) -> None:
        guild_roles = self.data.get("roles")
        roles = [
            DiscordRole(id=int(role["id"]), guild=self, data=role, cached_date=self.cached_date)
            for role in guild_roles
        ]
        DiscordRole.objects.bulk_create(roles, ignore_conflicts=True)
        DiscordRole.objects.bulk_update(roles, ["data", "cached_date"])

    @transaction.atomic
    def download_channels(self) -> None:
        try:
            guild_channels: List = self._fetch_channels()
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

    def _fetch_channels(self):
        r = requests.get(
            f"{DISCORD_BASE_URL}/guilds/{self.id}/channels",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
        )
        r.raise_for_status()
        return r.json()

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Guild")
        verbose_name_plural = _("Discord Guilds")


class DiscordGuildSettings(DiscordGuild):
    pass


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
    def name(self) -> str | None:
        return self.data.get("name")

    def refresh_from_api(self) -> None:
        logger.info(f"Updating {self}")
        try:
            self.data = self._fetch_one()
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")

    def _fetch_one(self):
        r = requests.get(
            f"{DISCORD_BASE_URL}/channels/{self.id}",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
        )
        r.raise_for_status()
        return r.json()

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

    def refresh_from_api(self) -> None:
        logger.info(f"Updating {self}")
        try:
            self.data = self._fetch_one()
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")

    def _fetch_one(self):
        r = requests.get(
            f"{DISCORD_BASE_URL}/channels/{self.id}",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
        )
        r.raise_for_status()
        return r.json()

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

        if len(nick) > 32:
            raise ValidationError("nick too long")
        logger.info(f"Renaming {self} to {nick}")
        r = requests.patch(
            f"{DISCORD_BASE_URL}/guilds/{self.guild.id}/members/{self.user.uid}",
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

    def __str__(self) -> str:
        return f"{self.display_name} in {self.guild}"

    def refresh_from_api(self) -> None:
        logger.info(f"Updating {self}")
        try:
            self.data = self._fetch_one()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
        else:
            if not self.user.extra_data:
                self.user.extra_data = self.data["user"]
                self.user.save()
            self.cached_date = timezone.now()

    def _fetch_one(self):
        r = requests.get(
            f"{DISCORD_BASE_URL}/guilds/{self.guild.id}/members/{self.user.uid}",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
        )
        r.raise_for_status()
        return r.json()

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Member")
        verbose_name_plural = _("Discord Members")
        unique_together = (("guild", "user"),)
