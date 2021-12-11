from allauth.socialaccount.admin import SocialAccountAdmin
from allauth.socialaccount.models import SocialAccount
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
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
