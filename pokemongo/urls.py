from django.urls import include, path, re_path
from django.views.generic import RedirectView
from pokemongo.views import LeaderboardView, CreateUpdateView, TrainerRedirectorView

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
    path("profile", TrainerRedirectorView, name="profile"),
    path("profile/id/<int:id>", TrainerRedirectorView, name="profile"),
    path("new", CreateUpdateView, name="update_stats"),
    path(
        "tools/update_stats/",
        RedirectView.as_view(pattern_name="trainerdex:update_stats", permanent=True),
    ),
    re_path(r"^(?P<nickname>[A-Za-z0-9]{3,15})\/?$", TrainerRedirectorView),
    re_path(
        r"^u\/(?P<nickname>[A-Za-z0-9]{3,15})\/?$", TrainerRedirectorView, name="profile_nickname"
    ),
    path(
        "",
        RedirectView.as_view(pattern_name="trainerdex:leaderboard", permanent=False),
        name="home",
    ),
]
