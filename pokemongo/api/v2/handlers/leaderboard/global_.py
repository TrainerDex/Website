from __future__ import annotations

from pokemongo.api.v2.handlers.leaderboard.base import BaseLeaderboardHandler


class GlobalLeaderboardHandler(BaseLeaderboardHandler):
    def get_leaderboard_title(self) -> str:
        return "Global Leaderboard"
