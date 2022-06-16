from __future__ import annotations

from typing import Type

from django.db.models import Q
from django.http import HttpRequest
from rest_framework.permissions import BasePermission

from core.models.discord import DiscordGuild


def IsInGuild(guild: DiscordGuild) -> Type[BasePermission]:
    class IsInGuild(BasePermission):
        def has_permission(self, request: HttpRequest, view: object) -> bool:
            if not request.user or not request.user.is_authenticated:
                return False

            if request.user.is_superuser:
                return True

            return request.user.socialaccount_set.filter(
                Q(guild_memberships__guild=guild) & Q(guild_memberships__active=True)
            ).exists()

    return IsInGuild
