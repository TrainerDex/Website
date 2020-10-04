from django.conf.urls import url
from django.urls import path
from pokemongo.api.v1.views import (
    TrainerListView,
    TrainerDetailView,
    UpdateListView,
    LatestUpdateView,
    UpdateDetailView,
    UserViewSet,
    SocialLookupView,
    LeaderboardView,
    DetailedLeaderboardView,
)

app_name = "trainerdex.api.1"

urlpatterns = [
    # /leaderboard/
    path("leaderboard/", LeaderboardView.as_view()),
    path("leaderboard//", DetailedLeaderboardView.as_view()),
    path("leaderboard//<str:stat>/", DetailedLeaderboardView.as_view()),
    path("leaderboard/discord/<int:guild>/", DetailedLeaderboardView.as_view()),
    path("leaderboard/discord/<int:guild>/<str:stat>/", DetailedLeaderboardView.as_view()),
    path("leaderboard/country/<str:country>/", DetailedLeaderboardView.as_view()),
    path("leaderboard/country/<str:country>/<str:stat>/", DetailedLeaderboardView.as_view()),
    path("leaderboard/community/<slug:community>/", DetailedLeaderboardView.as_view()),
    path("leaderboard/community/<slug:community>/<str:stat>/", DetailedLeaderboardView.as_view()),
    path("leaderboard/<str:stat>/", LeaderboardView.as_view()),
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
