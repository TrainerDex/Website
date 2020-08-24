import json
from typing import List, Optional

from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from django.contrib import admin, messages
from django.http import HttpRequest
from django.utils.safestring import mark_safe, SafeString
from django.utils.translation import gettext_lazy as _

from core.models import (
    DiscordGuild,
    DiscordGuildSettings,
    DiscordChannel,
    DiscordRole,
    DiscordGuildMembership,
    DiscordUser,
)

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter


def sync_members(modeladmin, request, queryset) -> None:
    for x in queryset:
        results = x.sync_members()
        for message in results["success"]:
            messages.success(request, message)
        for message in results["warning"]:
            messages.warning(request, message)


sync_members.short_description = _("Sync members with Discord")


def download_channels(modeladmin, request, queryset) -> None:
    for x in queryset:
        x.download_channels()


download_channels.short_description = _(
    "Download channels from Discord. Currently doesn't delete them."
)


class DiscordSettingsInline(admin.StackedInline):
    model = DiscordGuildSettings
    fieldsets = (
        ("Localization", {"fields": ("language", "timezone",)}),
        (
            "Welcomer",
            {"fields": ("renamer", "renamer_with_level", "renamer_with_level_format",)},
        ),
        ("TrainerDex", {"fields": ("monthly_gains_channel",)},),
    )
    verbose_name = _("Discord Server Settings")
    verbose_name_plural = _("Discord Server Settings")
    can_delete = False


@admin.register(DiscordGuild)
class DiscordGuildAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {"fields": ("id", "name", "owner",)}),
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
        self, request: HttpRequest, obj: Optional[DiscordGuild] = None
    ) -> List[str]:
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
        "last_login",
        "date_joined",
        "user",
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
    list_display = ["name", "type", "guild", "cached_date"]
    list_filter = ["guild", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[DiscordChannel] = None
    ) -> List[str]:
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
        "cached_date",
        "position",
    ]
    list_filter = ["guild", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[DiscordRole] = None
    ) -> List[str]:
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
        "cached_date",
    ]
    list_filter = ["guild", "active", "cached_date"]

    def get_readonly_fields(
        self, request: HttpRequest, obj: Optional[DiscordGuildMembership] = None
    ) -> List[str]:
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
