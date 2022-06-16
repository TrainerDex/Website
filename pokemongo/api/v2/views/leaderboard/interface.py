from __future__ import annotations

from abc import abstractmethod
from enum import Enum
from typing import Any

from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView


class LeaderboardMode(Enum):
    SNAPSHOT = "snapshot"
    GAIN = "gain"


class TrainerSubset(Enum):
    GLOBAL = "global"
    DISCORD = "discord"
    COUNTRY = "country"
    COMMUNITY = "community"


class iLeaderboardView(GenericAPIView):
    MODE: LeaderboardMode
    SUBSET: TrainerSubset

    def get(self, request: Request) -> Response:
        data = self.get_data(request)

        serializer: Serializer = self.get_serializer(data)
        return Response(serializer.data)

    @abstractmethod
    def get_data(self, request: Request) -> Any:
        pass
