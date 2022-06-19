from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from pokemongo.api.v2.serializers.leaderboard import (
    GainLeaderboardPaginatedResponseSerializer,
    SnapshotLeaderboardPaginatedResponseSerializer,
)


class GainLeaderboardPaginator(LimitOffsetPagination):
    default_limit = 25
    max_limit = 1000

    def get_paginated_response(self, data) -> Response:
        data["count"] = self.count
        data["next"] = self.get_next_link()
        data["previous"] = self.get_previous_link()

        serializer = GainLeaderboardPaginatedResponseSerializer(data)
        return Response(serializer.data)


class SnapshotLeaderboardPaginator(LimitOffsetPagination):
    default_limit = 25
    max_limit = 1000

    def get_paginated_response(self, data) -> Response:
        data["count"] = self.count
        data["next"] = self.get_next_link()
        data["previous"] = self.get_previous_link()

        serializer = SnapshotLeaderboardPaginatedResponseSerializer(data)
        return Response(serializer.data)
