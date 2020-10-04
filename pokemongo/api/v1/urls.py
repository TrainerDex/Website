from django.conf.urls import url
from pokemongo.api.v1.views import (
    TrainerListView,
    TrainerDetailView,
    UpdateListView,
    LatestUpdateView,
    UpdateDetailView,
    UserViewSet,
    SocialLookupView,
    LeaderboardView,
    DiscordLeaderboardView,
)

app_name = "trainerdex.api.1"

urlpatterns = [
    # /leaderboard/
    url(
        r"^leaderboard\/discord\/(?P<guild>[0-9]+)\/(?P<stat>[a-z_]+)\/$",
        DiscordLeaderboardView.as_view(),
    ),
    url(
        r"^leaderboard\/discord\/(?P<guild>[0-9]+)\/$",
        DiscordLeaderboardView.as_view(),
    ),
    url(r"^leaderboard\/$", LeaderboardView.as_view()),
    url(r"^leaderboard\/(?P<stat>[a-z_]+)\/$", LeaderboardView.as_view()),
    # /trainers/
    url(r"^trainers\/$", TrainerListView.as_view()),
    url(r"^trainers\/(?P<pk>[0-9]+)\/$", TrainerDetailView.as_view()),
    url(r"^trainers\/(?P<pk>[0-9]+)\/updates\/$", UpdateListView.as_view()),
    url(
        r"^trainers\/(?P<pk>[0-9]+)\/updates\/latest\/$",
        LatestUpdateView.as_view(),
        name="latest_update",
    ),
    url(
        r"^trainers\/(?P<pk>[0-9]+)\/updates\/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})\/$",
        UpdateDetailView.as_view(),
    ),
    # /users/
    url(r"^users\/$", UserViewSet.as_view({"get": "list", "post": "create"})),
    url(
        r"^users\/(?P<pk>[0-9]+)\/$",
        UserViewSet.as_view({"get": "retrieve", "patch": "partial_update"}),
    ),
    url(r"^users\/social\/$", SocialLookupView.as_view()),
]
