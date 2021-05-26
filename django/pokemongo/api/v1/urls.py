from django.urls import include, path
from pokemongo.api.v1.views import (
    DetailedLeaderboardView,
    LatestUpdateView,
    LeaderboardView,
    SocialLookupView,
    TrainerDetailView,
    TrainerListView,
    UpdateDetailView,
    UpdateListView,
    UserViewSet,
)

app_name = "trainerdex.api.1"

urlpatterns = [
    path(
        "leaderboard/",
        include(
            [
                path("", LeaderboardView.as_view()),
                path("v1.1/", DetailedLeaderboardView.as_view()),
                path("v1.1/<str:stat>/", DetailedLeaderboardView.as_view()),
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
                path("<str:stat>/", LeaderboardView.as_view()),
            ]
        ),
    ),
    path("trainers/", TrainerListView.as_view()),
    path(
        "trainers/<int:pk>/",
        include(
            [
                path("", TrainerDetailView.as_view()),
                path("updates/", UpdateListView.as_view()),
                path("updates/latest/", LatestUpdateView.as_view(), name="latest_update"),
                path("updates/<uuid:uuid>/", UpdateDetailView.as_view()),
            ]
        ),
    ),
    path("users/", UserViewSet.as_view({"get": "list", "post": "create"})),
    path("users/<int:pk>/", UserViewSet.as_view({"get": "retrieve", "patch": "partial_update"})),
    path("users/social/", SocialLookupView.as_view()),
]
