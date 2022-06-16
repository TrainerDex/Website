from __future__ import annotations
from abc import abstractmethod

from enum import Enum
from typing import Any

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.serializers import Serializer


class LeaderboardMode(Enum):
    SNAPSHOT = "snapshot"
    GAIN = "gain"


class TrainerSubset(Enum):
    GLOBAL = None
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


class LeaderboardView(APIView):
    def get(self, request: Request) -> Response:
        # Get the mode and subset from the request
        mode = LeaderboardMode(request.query_params.get("mode", "snapshot"))
        subset = TrainerSubset(request.query_params.get("subset", "global"))

        # Get the class for the given mode and subset
        # Loop over subclasses of iLeaderboardView to find the correct one
        for subclass in iLeaderboardView.__subclasses__():
            if subclass.MODE == mode and subclass.SUBSET == subset:
                return subclass().get(request)
            else:
                raise NotImplementedError
