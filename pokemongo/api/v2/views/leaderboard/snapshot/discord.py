from __future__ import annotations

from django.db.models import Q, QuerySet
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from requests import Response
from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from core.models.discord import DiscordGuild
from pokemongo.api.v2.views.leaderboard.interface import TrainerSubset
from pokemongo.api.v2.views.leaderboard.snapshot.interface import (
    iSnapshotLeaderboardView,
)
from pokemongo.models import Trainer


class DiscordSnapshotLeaderboardView(iSnapshotLeaderboardView):
    SUBSET = TrainerSubset.DISCORD

    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_leaderboard_title(self) -> str:
        return str(self.args["guild"])

    @staticmethod
    def get_guild(id: int | str) -> DiscordGuild:
        return DiscordGuild.objects.get(id=id)

    def parse_args(self, request: Request) -> None:
        super().parse_args(request)
        self.args["guild"] = self.get_guild(request.query_params.get("guild_id"))

    def get_trainer_subquery(self) -> QuerySet[Trainer]:
        queryset = super().get_trainer_subquery()
        return queryset.filter(owner__socialaccount__guilds__id=self.args["guild"].id)

    def in_guild(self, request: Request) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        return request.user.socialaccount_set.filter(
            Q(guild_memberships__guild=self.guild) & Q(guild_memberships__active=True)
        ).exists()

    def get(self, request: Request) -> Response:
        if not self.in_guild(request):
            raise PermissionDenied("You are not in this guild", status=403)

        return super().get(request)
