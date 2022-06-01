from __future__ import annotations

from django.db.models import Q
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models.discord import DiscordGuild
from pokemongo.api.v2.handlers.leaderboard import (
    DiscordLeaderboardHandler,
    GlobalLeaderboardHandler,
)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_global_leaderboard(request: Request) -> Response:
    return Response(GlobalLeaderboardHandler.get_data(request))


@api_view(["GET"])
@authentication_classes([OAuth2Authentication])
@permission_classes([IsAuthenticated])
def get_discord_leaderboard(request: Request, guild_id: id) -> Response:
    guild = DiscordGuild.objects.only("id", "data").get(id=guild_id)

    if (
        request.user.is_staff
        or request.user.socialaccount_set.filter(
            Q(guild_memberships__guild_id=guild.id) & Q(guild_memberships__active=True)
        ).exists()
    ):
        return Response(DiscordLeaderboardHandler.get_data(request, guild))

    raise PermissionDenied
