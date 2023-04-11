from typing import Union

from allauth.socialaccount.admin import SocialAccountAdmin as BaseSocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from django import forms
from django.contrib import admin
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


@admin.action(
    description=_("Refresh from API.")
)
def refresh_from_api(
    modeladmin: admin.ModelAdmin,
    request: HttpRequest,
    queryset: Union[
        QuerySet[DiscordGuild],
        QuerySet[DiscordChannel],
        QuerySet[DiscordRole],
        QuerySet[DiscordGuildMembership],
    ],
) -> None:
    for x in queryset:
        x.refresh_from_api()




class DiscordGuildAdminForm(forms.ModelForm):
    class Meta:
        model = DiscordGuild
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in [
            "roles_to_append_on_approval",
            "roles_to_remove_on_approval",
            "valor_role",
            "mystic_role",
            "instinct_role",
            "tl40_role",
            "tl50_role",
            "mod_role_ids",
        ]:
            self.fields[field].queryset = self.instance.roles.all()

        self.fields["leaderboard_channel"].queryset = self.instance.channels.filter(data__type=0)


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
            "Approvals",
            {
                "fields": (
                    "assign_roles_on_join",
                    "set_nickname_on_join",
                    "set_nickname_on_update",
                    "level_format",
                )
            },
        ),
        (
            "Roles",
            {
                "fields": (
                    "roles_to_append_on_approval",
                    "roles_to_remove_on_approval",
                    "valor_role",
                    "mystic_role",
                    "instinct_role",
                    "tl40_role",
                    "tl50_role",
                    "mod_role_ids",
                )
            },
        ),
        (
            "Leaderboards",
            {
                "fields": (
                    "weekly_leaderboards_enabled",
                    "leaderboard_channel",
                )
            },
        ),
        (
            "Debug",
            {"fields": ("data", "cached_date"), "classes": ("collapse",)},
        ),
    )
    form = DiscordGuildAdminForm
    search_fields = ["id", "data__name"]
    actions = [refresh_from_api]
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
    actions = [refresh_from_api]


@admin.register(DiscordChannel)
class DiscordChannelAdmin(admin.ModelAdmin):
    fields = ["guild", "data", "cached_date"]
    readonly_fields = fields
    autocomplete_fields = ["guild"]
    search_fields = ["guild", "data__name"]
    actions = [refresh_from_api]
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
    actions = [refresh_from_api]

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
    actions = [refresh_from_api]

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
