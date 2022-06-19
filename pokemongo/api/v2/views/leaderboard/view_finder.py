from __future__ import annotations

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from pokemongo.api.v2.views.leaderboard.interface import LeaderboardMode, TrainerSubset
from pokemongo.api.v2.views.leaderboard.snapshot.interface import (
    iSnapshotLeaderboardView,
)


class LeaderboardViewFinder(APIView):
    def get(self, request: Request) -> Response:
        # Get the mode and subset from the request
        mode = LeaderboardMode(request.query_params.get("mode", "snapshot"))
        subset = TrainerSubset(request.query_params.get("subset", "global"))

        # Get the class for the given mode and subset
        # Loop over subclasses of iLeaderboardView to find the correct one
        if mode == LeaderboardMode.SNAPSHOT:
            iklass = iSnapshotLeaderboardView

        for subclass in iklass.__subclasses__():
            if subclass.SUBSET == subset:
                return subclass.as_view()(request._request)

        raise NotImplementedError
