from django.urls import include, path

from djangorestversioning.versioning import VersionedEndpoint
from rest_framework.views import APIView


class LeaderboardView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.leaderboard.LeaderboardView",
        2.0: "pokemongo.api.v2.leaderboard.LeaderboardView",
    }


class DetailedLeaderboardView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.leaderboard.DetailedLeaderboardView",
        2.0: "pokemongo.api.v2.leaderboard.LeaderboardView",
    }


urlpatterns = [
    path("discord/<int:guild>/", DetailedLeaderboardView.as_view()),
    path(
        "discord/<int:guild>/<str:stat>/",
        DetailedLeaderboardView.as_view(),
    ),
    path("country/<str:country>/", DetailedLeaderboardView.as_view()),
    path(
        "country/<str:country>/<str:stat>/",
        DetailedLeaderboardView.as_view(),
    ),
    path("community/<slug:community>/", DetailedLeaderboardView.as_view()),
    path(
        "community/<slug:community>/<str:stat>/",
        DetailedLeaderboardView.as_view(),
    ),
    path("", LeaderboardView.as_view()),
    path("<str:stat>/", LeaderboardView.as_view()),
]
