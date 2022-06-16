from __future__ import annotations

from django.db.models import QuerySet
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.request import Request

from core.models.discord import DiscordGuild
from core.permissions.guild import IsInGuild
from pokemongo.api.v2.views.leaderboard.interface import TrainerSubset
from pokemongo.api.v2.views.leaderboard.snapshot.interface import iSnapshotLeaderboardView
from pokemongo.models import Trainer


class DiscordSnapshotLeaderboardView(iSnapshotLeaderboardView):
    SUBSET = TrainerSubset.DISCORD

    authentication_classes = [OAuth2Authentication, SessionAuthentication]
    permission_classes = [IsInGuild]

    def get_leaderboard_title(self, arguments: dict) -> str:
        return str(arguments["guild"])

    @staticmethod
    def get_guild(id: int | str) -> DiscordGuild:
        return DiscordGuild.objects.get(id=id)

    def parse_args(self, request: Request) -> dict:
        arguments = super().parse_args(request)
        arguments["guild"] = self.get_guild(request.query_params.get("guild_id"))
        return arguments

    def get_trainer_subquery(self, arguments: dict) -> QuerySet[Trainer]:
        queryset = super().get_trainer_subquery()
        return queryset.filter(owner__socialaccount__guilds__id=arguments["guild"].id)
