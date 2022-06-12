from __future__ import annotations
from datetime import datetime

from django.db.models import Q
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from core.models.discord import DiscordGuild
from pokemongo.api.v2.querysets import get_discord_trainer_query, get_queryset_for_diffboard


@api_view(["GET"])
@authentication_classes([])
# @authentication_classes([OAuth2Authentication])
# @permission_classes([IsAuthenticated])
@permission_classes([])
def get_discord_diffboard(request: Request, guild_id: id) -> Response:
    assert DiscordGuild.objects.filter(id=guild_id).exists()

    dt0 = datetime.fromisoformat(dt0) if (dt0 := request.query_params.get("dt0", None)) else None
    dt1 = datetime.fromisoformat(dt1) if (dt1 := request.query_params.get("dt1", None)) else None
    dt2 = datetime.fromisoformat(dt2) if (dt2 := request.query_params.get("dt2", None)) else None
    stat = request.query_params.get("stat", "total_xp")

    assert dt1 is not None
    assert dt2 is not None

    if (
        request.user.is_authenticated
        and (
            request.user.is_staff
            or request.user.socialaccount_set.filter(
                Q(guild_memberships__guild_id=guild_id) & Q(guild_memberships__active=True)
            ).exists()
        )
    ) or True:
        trainers = get_discord_trainer_query(dt2, guild_id)
        queryset = get_queryset_for_diffboard(trainers, dt1, dt2, stat, dt0)
        return Response(queryset, status=200)

    raise PermissionDenied
