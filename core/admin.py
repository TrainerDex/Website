from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from django.contrib import admin, messages
from django.db.models import Prefetch, QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from core.models.discord import (
    DiscordChannel,
    DiscordGuild,
    DiscordGuildMembership,
    DiscordRole,
    DiscordUser,
)
from core.models.main import Service, ServiceStatus, StatusChoices


def sync_members(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[DiscordGuild]
) -> None:
    for x in queryset:
        messages.success(request, x.sync_members())


sync_members.short_description = _("Sync members with Discord")


def download_channels(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[DiscordGuild]
) -> None:
    for x in queryset:
        x.download_channels()


download_channels.short_description = _(
    "Download channels from Discord. Currently doesn't delete them."
)


@admin.register(DiscordGuild)
class DiscordGuildAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "id",
                    "name",
                    "owner",
                )
            },
        ),
        (
            "Localization",
            {
                "fields": (
                    "language",
                    "timezone",
                )
            },
        ),
        (
            "Welcomer",
            {
                "fields": (
                    "renamer",
                    "renamer_with_level",
                    "renamer_with_level_format",
                )
            },
        ),
        (
            "TrainerDex",
            {"fields": ("monthly_gains_channel",)},
        ),
        (
            "Debug",
            {"fields": ("data", "cached_date"), "classes": ("collapse",)},
        ),
    )
    search_fields = ["id", "data__name"]
    actions = [sync_members, download_channels]
    list_display = [
        "name",
        "id",
        "_outdated",
        "has_data",
        "has_access",
        "cached_date",
    ]

    def get_readonly_fields(
        self, request: HttpRequest, obj: DiscordGuild | None = None
    ) -> list[str]:
        if obj:
            return ["id", "name", "owner", "data", "cached_date"]
        else:
            return ["name", "owner", "data", "cached_date"]


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    fields = [
        "user",
        "uid",
        "last_login",
        "date_joined",
        "extra_data",
    ]
    search_fields = [
        "user__username",
        "uid",
    ]
    list_display = [
        "__str__",
        "uid",
        "user",
        "has_data",
        "last_login",
        "date_joined",
    ]
    readonly_fields = ["uid", "last_login", "date_joined", "extra_data"]


@admin.register(DiscordChannel)
class DiscordChannelAdmin(admin.ModelAdmin):
    fields = ["guild", "data", "cached_date"]
    readonly_fields = fields
    autocomplete_fields = ["guild"]
    search_fields = ["guild", "data__name"]
    list_display = ["name", "guild", "has_data", "cached_date"]
    list_filter = ["guild", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: DiscordChannel | None = None
    ) -> list[str]:
        if obj:
            return self.fields
        else:
            return ["data", "cached_date"]


@admin.register(DiscordRole)
class DiscordRoleAdmin(admin.ModelAdmin):
    fields = ["guild", "data", "cached_date"]
    readonly_fields = fields
    autocomplete_fields = ["guild"]
    search_fields = ["guild", "id"]
    list_display = [
        "name",
        "guild",
        "has_data",
        "cached_date",
    ]
    list_filter = ["guild", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: DiscordRole | None = None
    ) -> list[str]:
        if obj:
            return self.fields
        else:
            return ["data", "cached_date"]


@admin.register(DiscordGuildMembership)
class DiscordGuildMembershipAdmin(admin.ModelAdmin):
    fields = [
        "guild",
        "user",
        "data",
        "cached_date",
        "active",
        "nick_override",
    ]
    autocomplete_fields = ["guild", "user"]
    search_fields = [
        "guild__data__name",
        "guild__id",
        "user__user__username",
        "user__user__trainer__nickname__nickname",
        "data__nick",
        "data__user__username",
    ]
    list_display = [
        "user",
        "__str__",
        "active",
        "has_data",
        "cached_date",
    ]
    list_filter = ["guild", "active", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: DiscordGuildMembership | None = None
    ) -> list[str]:
        if obj:
            return ["guild", "user", "data", "cached_date"]
        else:
            return ["data", "cached_date"]


admin.site.unregister(SocialAccount)


@admin.register(SocialAccount)
class SocialAccountAdmin(BaseSocialAccountAdmin):
    search_fields = ["user", "uid"]


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("name", "status")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Service]:
        return (
            super()
            .get_queryset(request)
            .prefetch_related(
                Prefetch(
                    "statuses",
                    ServiceStatus.objects.order_by("-created_at"),
                    to_attr="statuses_ordered",
                )
            )
        )

    def status(self, obj: Service) -> str:
        try:
            return obj.statuses_ordered[0].status
        except IndexError:
            return StatusChoices.UNKNOWN.value


@admin.register(ServiceStatus)
class NameAdmin(admin.ModelAdmin):
    list_display = ("service", "status", "created_at")
