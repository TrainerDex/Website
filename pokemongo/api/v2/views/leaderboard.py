from __future__ import annotations

from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from pokemongo.api.v2.handlers.leaderboard import GlobalLeaderboardHandler


@api_view(["GET"])
def get_global_leaderboard(request: Request) -> Response:
    return Response(GlobalLeaderboardHandler.get_data(request))
