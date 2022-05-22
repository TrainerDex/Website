import json
from datetime import datetime

from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from django.contrib import admin, messages
from django.db.models import Prefetch, QuerySet
from django.http import HttpRequest
from django.utils.safestring import SafeString, mark_safe
from django.utils.translation import gettext_lazy as _
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import JsonLexer

from core.models import (
    DiscordChannel,
    DiscordGuild,
    DiscordGuildMembership,
    DiscordGuildSettings,
    DiscordRole,
    DiscordUser,
    Service,
    ServiceStatus,
    StatusChoices,
)


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


class DiscordSettingsInline(admin.StackedInline):
    model = DiscordGuildSettings
    fieldsets = (
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
    )
    verbose_name = _("Discord Server Settings")
    verbose_name_plural = _("Discord Server Settings")
    can_delete = False


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
            "Debug",
            {"fields": ("data_prettified", "cached_date"), "classes": ("collapse",)},
        ),
    )
    inlines = [DiscordSettingsInline]
    search_fields = ["id", "data__name"]
    actions = [sync_members, download_channels]
    list_display = [
        "name",
        "id",
        "_outdated",
        "has_data",
        "has_access",
        "owner",
        "cached_date",
    ]

    def get_readonly_fields(
        self, request: HttpRequest, obj: DiscordGuild | None = None
    ) -> list[str]:
        if obj:
            return ["id", "name", "owner", "data_prettified", "cached_date"]
        else:
            return ["name", "owner", "data_prettified", "cached_date"]

    def data_prettified(self, instance: DiscordGuild) -> SafeString:
        """Function to display pretty version of our data"""
        response = json.dumps(instance.data, sort_keys=True, indent=2)
        formatter = HtmlFormatter(style="colorful")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    data_prettified.short_description = "data"


@admin.register(DiscordUser)
class DiscordUserAdmin(admin.ModelAdmin):
    fields = [
        "user",
        "uid",
        "last_login",
        "date_joined",
        "data_prettified",
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
    readonly_fields = ["uid", "last_login", "date_joined", "data_prettified"]

    def data_prettified(self, instance: DiscordUser) -> SafeString:
        """Function to display pretty version of our data"""
        response = json.dumps(instance.extra_data, sort_keys=True, indent=2)
        formatter = HtmlFormatter(style="colorful")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    data_prettified.short_description = "data"


@admin.register(DiscordChannel)
class DiscordChannelAdmin(admin.ModelAdmin):
    fields = ["guild", "data_prettified", "cached_date"]
    readonly_fields = fields
    autocomplete_fields = ["guild"]
    search_fields = ["guild", "data__name"]
    list_display = ["name", "type", "guild", "has_data", "cached_date"]
    list_filter = ["guild", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: DiscordChannel | None = None
    ) -> list[str]:
        if obj:
            return self.fields
        else:
            return ["data_prettified", "cached_date"]

    def data_prettified(self, instance: DiscordChannel) -> SafeString:
        """Function to display pretty version of our data"""
        response = json.dumps(instance.data, sort_keys=True, indent=2)
        formatter = HtmlFormatter(style="colorful")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    data_prettified.short_description = "data"


@admin.register(DiscordRole)
class DiscordRoleAdmin(admin.ModelAdmin):
    fields = ["guild", "data_prettified", "cached_date"]
    readonly_fields = fields
    autocomplete_fields = ["guild"]
    search_fields = ["guild", "id"]
    list_display = [
        "name",
        "guild",
        "has_data",
        "cached_date",
        "position",
    ]
    list_filter = ["guild", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: DiscordRole | None = None
    ) -> list[str]:
        if obj:
            return self.fields
        else:
            return ["data_prettified", "cached_date"]

    def data_prettified(self, instance: DiscordRole) -> SafeString:
        """Function to display pretty version of our data"""
        response = json.dumps(instance.data, sort_keys=True, indent=2)
        formatter = HtmlFormatter(style="colorful")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    data_prettified.short_description = "data"


@admin.register(DiscordGuildMembership)
class DiscordGuildMembershipAdmin(admin.ModelAdmin):
    fields = [
        "guild",
        "user",
        "data_prettified",
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
            return ["guild", "user", "data_prettified", "cached_date"]
        else:
            return ["data_prettified", "cached_date"]

    def data_prettified(self, instance: DiscordGuildMembership) -> SafeString:
        """Function to display pretty version of our data"""
        response = json.dumps(instance.data, sort_keys=True, indent=2)
        formatter = HtmlFormatter(style="colorful")
        response = highlight(response, JsonLexer(), formatter)
        style = "<style>" + formatter.get_style_defs() + "</style><br>"
        return mark_safe(style + response)

    data_prettified.short_description = "data"


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
