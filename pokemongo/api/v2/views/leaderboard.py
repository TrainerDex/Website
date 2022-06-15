from __future__ import annotations
from datetime import date

from attrs import NOTHING
from attrs import define, field, validators
from django.db.models import Q
from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


from core.models.discord import DiscordGuild
from pokemongo.api.v2.handlers.leaderboard import (
    DiscordLeaderboardHandler,
    GlobalLeaderboardHandler,
)
from pokemongo.shortcuts import UPDATE_SORTABLE_FIELDS


@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def get_global_leaderboard(request: Request) -> Response:
    return Response(GlobalLeaderboardHandler.get_data(request))


@api_view(["GET"])
@authentication_classes([OAuth2Authentication, SessionAuthentication])
@permission_classes([IsAuthenticated])
def get_discord_leaderboard(request: Request, guild_id: id) -> Response:
    guild = DiscordGuild.objects.only("id", "data").get(id=guild_id)

    if request.user.is_authenticated and (
        request.user.is_staff
        or request.user.socialaccount_set.filter(
            Q(guild_memberships__guild_id=guild.id) & Q(guild_memberships__active=True)
        ).exists()
    ):
        return Response(DiscordLeaderboardHandler.get_data(request, guild))

    raise PermissionDenied


@define
class LeaderboardParams:
    stat: str = field(default="total_xp", validator=validators.in_(UPDATE_SORTABLE_FIELDS))
    start_date: date = field(default=NOTHING, converter=date.fromisoformat)
    end_date: date = field(default=NOTHING, converter=date.fromisoformat)
    date: date = field(default=NOTHING, converter=date.fromisoformat)
    mode: str = field(default="snapshot", validator=validators.in_(["snapshot", "gain"]))
    primary_filter_type: str = field(
        default="all", validator=validators.in_(["all", "discord", "community", "country"])
    )
    primary_filter_value: str = field(default=NOTHING)


class LeaderboardView(APIView):
    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def parse_query_params(self, request: Request) -> LeaderboardParams:
        self.parameters = LeaderboardParams(**request.query_params)
        return self.parameters

    def get(self, request: Request) -> Response:
        self.parse_query_params(request)

        self.get_trainer_subquery()
        self.get_subquery()
        self.get_query()

        data = self.serialize_data()
        return Response(data)
