from django.urls import include, path
from django.views.generic import RedirectView

from pokemongo.views import CreateUpdateView, LeaderboardView, UserRedirectorView

app_name = "trainerdex"

urlpatterns = [
    path(
        "leaderboard/",
        include(
            [
                path("", LeaderboardView, name="leaderboard"),
                path("country/<str:country>", LeaderboardView, name="leaderboard"),
                path("community/<slug:community>", LeaderboardView, name="leaderboard"),
            ]
        ),
    ),
    path("profile/", UserRedirectorView, name="profile"),
    path("profile/id/<int:id>/", UserRedirectorView, name="profile"),
    path("new/", CreateUpdateView, name="update_stats"),
    path(
        "tools/update_stats/",
        RedirectView.as_view(pattern_name="trainerdex:update_stats", permanent=True),
    ),
    path("u/<str:nickname>/", UserRedirectorView, name="profile"),
    path(
        "",
        RedirectView.as_view(pattern_name="trainerdex:leaderboard", permanent=False),
        name="home",
    ),
]
