from typing import Any, Dict, List, Optional, Tuple
from allauth.socialaccount.admin import SocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from common.models import FeedPost, User, UsernameHistory

admin.site.register(FeedPost)
admin.site.register(UsernameHistory)
admin.site.unregister(SocialAccount)


@admin.register(SocialAccount)
class ZapdosSocialAccountAdmin(SocialAccountAdmin):
    search_fields = ["user", "uid"]


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "timezone",
                    "country",
                )
            },
        ),
        (
            _("Pokémon Go"),
            {
                "fields": (
                    "trainer_code",
                    "daily_goal",
                    "total_goal",
                    "pogo_date_created",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_public",
                    "is_perma_banned",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (
            _("Important dates"),
            {
                "fields": (
                    "last_login",
                    "date_joined",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
        (
            _("Pokémon Go"),
            {
                "fields": (
                    "trainer_code",
                    "daily_goal",
                    "total_goal",
                    "pogo_date_created",
                )
            },
        ),
    )

    list_display = (
        "username",
        "faction",
        "is_banned",
        "is_public",
        "is_verified",
        "country",
        "timezone",
    )
    list_filter = (
        "last_caught_cheating",
        "is_public",
        "is_perma_banned",
        "is_verified",
    )
    search_fields = (
        "first_name",
        "username",
    )
    ordering = ("username",)
