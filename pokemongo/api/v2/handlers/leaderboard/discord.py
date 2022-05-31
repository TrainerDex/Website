from __future__ import annotations

from django.contrib.postgres.fields import ArrayField
from django.db.models import F, Subquery, CharField, QuerySet, Q
from django.db.models.functions import Cast
from rest_framework.request import Request

from core.models.discord import DiscordGuild
from pokemongo.api.v2.handlers.leaderboard.base import BaseLeaderboardHandler
from pokemongo.models import Trainer


class DiscordLeaderboardHandler(BaseLeaderboardHandler):
    def __init__(self, request: Request, *args, discord_guild: DiscordGuild, **kwargs) -> None:
        self.discord_guild = discord_guild
        super().__init__(request, *args, **kwargs)

    def get_leaderboard_title(self) -> str:
        return str(self.discord_guild)

    def get_trainer_subquery(self) -> QuerySet[Trainer]:
        return (
            super()
            .get_trainer_subquery()
            .filter(owner__socialaccount__guilds__id=self.discord_guild.id)
        )
