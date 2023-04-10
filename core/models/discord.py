from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import List

import requests
from allauth.socialaccount.models import SocialAccount, SocialApp
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from psqlextra.manager import PostgresManager
from psqlextra.models import PostgresModel

logger = logging.getLogger(f"trainerdex.website.{__name__}")

DISCORD_BASE_URL = "https://discord.com/api/v10"


class DiscordGuild(PostgresModel):
    id: int = models.BigIntegerField(primary_key=True, verbose_name="ID")
    data: dict | list = models.JSONField(null=True, blank=True)
    cached_date: datetime = models.DateTimeField(auto_now_add=True)
    has_access: bool = models.BooleanField(default=False)

    name: str = models.CharField(max_length=100, null=True, blank=True)
    owner_id: int = models.BigIntegerField(null=True, blank=True)

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
        max_length=255,
    )

    assign_roles_on_join: bool = models.BooleanField(
        default=True,
    )
    set_nickname_on_join: bool = models.BooleanField(
        default=True,
    )
    set_nickname_on_update: bool = models.BooleanField(
        default=True,
    )
    level_format: str = models.CharField(
        default="int",
        verbose_name=_("Level Indicator format"),
        max_length=50,
        choices=[("none", "None"), ("int", "40"), ("circled_level", "㊵")],
    )

    roles_to_append_on_approval: List["DiscordRole"] = models.ManyToManyField(
        "DiscordRole",
        db_constraint=False,
        blank=True,
        related_name="+",
    )
    roles_to_remove_on_approval: List["DiscordRole"] = models.ManyToManyField(
        "DiscordRole",
        db_constraint=False,
        blank=True,
        related_name="+",
    )
    mystic_role: "DiscordRole" | None = models.ForeignKey(
        "DiscordRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    valor_role: "DiscordRole" | None = models.ForeignKey(
        "DiscordRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    instinct_role: "DiscordRole" | None = models.ForeignKey(
        "DiscordRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    tl40_role: "DiscordRole" | None = models.ForeignKey(
        "DiscordRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )
    tl50_role: "DiscordRole" | None = models.ForeignKey(
        "DiscordRole",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
    )

    weekly_leaderboards_enabled: bool = models.BooleanField(
        default=False,
    )
    leaderboard_channel: "DiscordChannel" | None = models.ForeignKey(
        "DiscordChannel",
        db_constraint=False,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        limit_choices_to=models.Q(data__type=0),
    )

    mod_role_ids: List["DiscordRole"] = models.ManyToManyField(
        "DiscordRole",
        db_constraint=False,
        blank=True,
        related_name="+",
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
    def owner(self) -> int:
        return self.owner_id or self.data.get("owner_id")

    def __str__(self) -> str:
        return self.name or f"Discord Guild with ID {self.id}"

    @transaction.atomic
    def refresh_from_api(self) -> None:
        if data := self._fetch_one():
            self.data = data
            self.cached_date = timezone.now()

        self.has_access = data is not None

        self.save()
        if data:
            self.sync_roles()
            self.sync_members()
            self.sync_channels()

    def _fetch_one(self) -> dict | None:
        for provider in SocialApp.objects.filter(provider="discord"):
            r = requests.get(
                f"{DISCORD_BASE_URL}/guilds/{self.id}",
                headers={"Authorization": f"Bot {provider.key}"},
            )
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                continue
            return r.json()

    @transaction.atomic
    def sync_members(self) -> str | dict[str, list[str]]:  # Is this a bug?
        try:
            guild_api_members = self._fetch_guild_members()
            cache_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
            return {"warning": ["Failed to get server information from Discord"]}
        existing_social_accounts: dict[str, DiscordUser] = {
            str(user.uid): user for user in DiscordUser.objects.all()
        }
        existing_discord_memberships: dict[str, DiscordGuildMembership] = {
            str(membership.user.uid): membership
            for membership in DiscordGuildMembership.objects.filter(guild=self).prefetch_related(
                "user"
            )
        }

        new_discord_memberships: list[DiscordGuildMembership] = list()
        amended_discord_memberships: set[DiscordGuildMembership] = set()

        amended_user_data: set[DiscordUser] = set()

        for member_data in guild_api_members:
            if (user_id := str(member_data["user"]["id"])) in existing_social_accounts.keys():
                if membership := existing_discord_memberships.get(user_id):
                    membership.data = member_data
                    membership.cached_date = cache_date
                    amended_discord_memberships.add(membership)
                else:
                    membership = DiscordGuildMembership(
                        guild=self,
                        user=existing_social_accounts[user_id],
                        active=True,
                        data=member_data,
                        cached_date=cache_date,
                    )
                    new_discord_memberships.append(membership)

                if not membership.user.extra_data:
                    membership.user.extra_data = member_data["user"]
                    amended_user_data.add(membership.user)

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

        DiscordUser.objects.bulk_update(amended_user_data, ["extra_data"])

        return _("Succesfully updated {x} of {y} {guild} members").format(
            x=DiscordGuildMembership.objects.filter(guild=self).count(),
            y=len(guild_api_members),
            guild=self,
        )

    def _fetch_guild_members(self):
        previous = None
        result = []

        for provider in SocialApp.objects.filter(provider="discord"):
            while True:
                r = requests.get(
                    f"{DISCORD_BASE_URL}/guilds/{self.id}/members",
                    headers={"Authorization": f"Bot {provider.key}"},
                    params={"limit": 1000, "after": previous},
                )
                if r.status_code == 403:
                    break
                if r.status_code == 429:
                    time.sleep(
                        float(r.headers.get("Retry-After", r.headers["X-RateLimit-Reset-After"]))
                    )
                    continue
                r.raise_for_status()
                if data := r.json():
                    result += data
                    previous = result[-1]["user"]["id"]
                else:
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
        DiscordRole.objects.filter(guild=self).exclude(id__in=[x.id for x in roles]).delete()

    @transaction.atomic
    def sync_channels(self) -> None:
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
            DiscordChannel.objects.filter(guild=self).exclude(
                id__in=[x.id for x in channels]
            ).delete()

    def _fetch_channels(self):
        for provider in SocialApp.objects.filter(provider="discord"):
            r = requests.get(
                f"{DISCORD_BASE_URL}/guilds/{self.id}/channels",
                headers={"Authorization": f"Bot {provider.key}"},
            )
            try:
                r.raise_for_status()
            except requests.exceptions.HTTPError:
                continue
            return r.json()

    def clean(self) -> None:
        self.refresh_from_api()

    class Meta:
        verbose_name = _("Discord Guild")
        verbose_name_plural = _("Discord Guilds")


class DiscordChannel(PostgresModel):
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
        try:
            self.data = self._fetch_one()
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
        else:
            self.save()

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


class DiscordRole(PostgresModel):
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
        return self.name

    @property
    def name(self) -> str | None:
        return self.data.get("name")

    def refresh_from_api(self) -> None:
        try:
            self.data = self._fetch_one()
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
        else:
            self.save()

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


class DiscordUserManager(PostgresManager):
    def get_queryset(self) -> models.QuerySet[DiscordUser]:
        return super(DiscordUserManager, self).get_queryset().filter(provider="discord")

    def create(self, **kwargs) -> DiscordUser:
        kwargs.update({"provider": "discord"})
        return super(DiscordUserManager, self).create(**kwargs)


class DiscordUser(SocialAccount):
    objects = DiscordUserManager()

    def __str__(self) -> str:
        return self.get_provider_account().to_str()

    def has_data(self) -> bool:
        return bool(self.extra_data)

    has_data.boolean = True
    has_data.short_description = _("got data")

    class Meta:
        proxy = True
        verbose_name = _("Discord User")
        verbose_name_plural = _("Discord Users")


class DiscordGuildMembership(PostgresModel):
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
        requests.patch(
            f"{DISCORD_BASE_URL}/guilds/{self.guild.id}/members/{self.user.uid}",
            headers={"Authorization": f"Bot {settings.DISCORD_TOKEN}"},
            json={"nick": nick},
        )
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
        try:
            self.data = self._fetch_one()
            self.cached_date = timezone.now()
        except requests.exceptions.HTTPError:
            logger.exception("Failed to get server information from Discord")
        else:
            self.save()
            if not self.user.extra_data:
                self.user.extra_data = self.data["user"]
                self.user.save()

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
