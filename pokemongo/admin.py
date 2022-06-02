from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from django.contrib import admin, messages
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as pgettext

from pokemongo.models import (
    Community,
    CommunityMembershipDiscord,
    Nickname,
    ProfileBadge,
    ProfileBadgeHoldership,
    Trainer,
    Update,
)
from pokemongo.shortcuts import BATTLE_HUB_STATS, STANDARD_MEDALS, UPDATE_FIELDS_TYPES

if TYPE_CHECKING:
    from config.abstract_models import PrivateModel


def sync_members(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[Community]
):
    for x in queryset:
        for y in x.memberships_discord.filter(communitymembershipdiscord__sync_members=True):
            results = y.sync_members()
            for message in results["success"]:
                messages.success(request, message)
            for message in results["warning"]:
                messages.warning(request, message)


sync_members.short_description = _("Sync Members for all eligible Discords")


def soft_delete(
    modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[PrivateModel]
):
    delete_time = now()
    counter = Counter()
    for obj in queryset:
        counter += obj.soft_delete(updated_at=delete_time)
    if counter:
        objects_deleted_str = ", ".join(f"{count} {model}" for model, count in counter.items())
    else:
        objects_deleted_str = "No"
    messages.info(request, f"{objects_deleted_str} object(s) deleted")


soft_delete.short_description = _("Soft Delete")


def undelete(modeladmin: admin.ModelAdmin, request: HttpRequest, queryset: QuerySet[PrivateModel]):
    restore_time = now()
    counter = Counter()
    for obj in queryset:
        counter += obj.undelete(updated_at=restore_time)

    if counter:
        objects_restored_str = ", ".join(f"{count} {model}" for model, count in counter.items())
    else:
        objects_restored_str = "No"
    messages.info(request, f"{objects_restored_str} object(s) restored")


undelete.short_description = _("Restore (Undelete)")


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):

    search_fields = ("name", "short_description", "handle")
    autocomplete_fields = ["memberships_personal", "memberships_discord"]
    actions = [sync_members]


@admin.register(CommunityMembershipDiscord)
class CommunityMembershipDiscordAdmin(admin.ModelAdmin):

    autocomplete_fields = ["community", "discord"]


@admin.register(ProfileBadge)
class ProfileBadgeAdmin(admin.ModelAdmin):

    autocomplete_fields = ["members"]
    search_fields = ("title", "slug")


@admin.register(ProfileBadgeHoldership)
class ProfileBadgeHoldershipAdmin(admin.ModelAdmin):

    autocomplete_fields = ["trainer", "badge", "awarded_by"]
    search_fields = ("trainer__nickname__nickname", "badge__title", "badge__slug")


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):

    autocomplete_fields = ["trainer"]
    list_display = (
        "trainer",
        "total_xp",
        "update_time",
        "created_at",
        "has_modified_extra_fields",
    )
    search_fields = ("trainer__nickname__nickname", "trainer__owner__username")
    ordering = ("-update_time",)
    date_hierarchy = "update_time"

    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
        "is_deleted",
        "deleted_at",
    )
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "uuid",
                    "created_at",
                    "updated_at",
                    "is_deleted",
                    "deleted_at",
                ]
            },
        ),
        (
            Update._meta.verbose_name,
            {
                "fields": [
                    "trainer",
                    "update_time",
                    "data_source",
                    "screenshot",
                    "double_check_confirmation",
                ]
            },
        ),
        (
            pgettext("profile_category_stats", "Stats"),
            {
                "fields": [
                    "total_xp",
                    "pokedex_caught",
                    "pokedex_seen",
                    "gym_gold",
                ],
            },
        ),
        (
            pgettext("profile_category_medals", "Medals"),
            {"fields": STANDARD_MEDALS},
        ),
        (
            pgettext("battle_hub_category_league", "GO Battle League"),
            {"fields": BATTLE_HUB_STATS},
        ),
        (
            pgettext("pokemon_info_type", "Type"),
            {"fields": UPDATE_FIELDS_TYPES},
        ),
    ]
    actions = [soft_delete, undelete]


@admin.register(Nickname)
class NicknameAdmin(admin.ModelAdmin):

    search_fields = (
        "nickname",
        "trainer__owner__first_name",
        "trainer__owner__username",
    )
    list_display = (
        "nickname",
        "trainer",
        "active",
    )
    list_filter = ("active",)
    list_display_links = ("nickname",)
    autocomplete_fields = ["trainer"]


@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):

    autocomplete_fields = [
        "owner",
    ]
    list_display = (
        "nickname",
        "faction",
        "currently_banned",
        "is_on_leaderboard",
        "is_verified",
        "awaiting_verification",
    )
    list_filter = (
        "faction",
        "last_cheated",
        "statistics",
        "verified",
    )
    search_fields = (
        "nickname__nickname",
        "owner__first_name",
        "owner__username",
    )
    ordering = ("nickname__nickname", "pk")
    readonly_fields = (
        "uuid",
        "created_at",
        "updated_at",
        "is_deleted",
        "deleted_at",
    )
    actions = [soft_delete, undelete]

    fieldsets = (
        (
            None,
            {
                "fields": [
                    "uuid",
                    "created_at",
                    "updated_at",
                    "is_deleted",
                    "deleted_at",
                ]
            },
        ),
        (
            Trainer._meta.verbose_name,
            {
                "fields": (
                    "owner",
                    "faction",
                    "start_date",
                    "daily_goal",
                    "total_goal",
                    "trainer_code",
                )
            },
        ),
        (_("Reports"), {"fields": ("last_cheated", "verified", "verification")}),
        (
            _("Leaderboard"),
            {"fields": ("country_iso", "statistics", "legacy_40")},
        ),
    )
