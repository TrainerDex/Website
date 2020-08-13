from django.conf.urls import url
from pokemongo.views import (
    LeaderboardView,
    CreateUpdateView,
    TrainerRedirectorView,
)

app_name = "trainerdex"

urlpatterns = [
    url(r"^leaderboard\/?$", LeaderboardView, name="leaderboard"),
    url(
        r"^leaderboard\/continent\/(?P<continent>[\w]+)\/?$",
        LeaderboardView,
        name="leaderboard",
    ),
    url(
        r"^leaderboard\/country\/(?P<country>[\w]+)\/?$",
        LeaderboardView,
        name="leaderboard",
    ),
    url(
        r"^leaderboard\/country\/(?P<country>[\w]+)\/(?P<region>[\w\d]+)\/?$",
        LeaderboardView,
        name="leaderboard",
    ),
    url(
        r"^leaderboard\/community\/(?P<community>[\w\d]+)\/?$",
        LeaderboardView,
        name="leaderboard",
    ),
    url(r"^profile\/?$", TrainerRedirectorView, name="profile"),
    url(
        r"^profile\/username\/(?P<nickname>[\w\d]{3,15})\/?$",
        TrainerRedirectorView,
        name="profile",
    ),
    url(
        r"^profile\/nickname\/(?P<nickname>[\w\d]{3,15})\/?$",
        TrainerRedirectorView,
        name="profile",
    ),
    url(r"^profile\/id\/(?P<id>[\d]+)\/?$", TrainerRedirectorView, name="profile"),
    url(r"^tools\/update_stats\/?$", CreateUpdateView, name="update_stats"),
    url(r"^(?P<nickname>[A-Za-z0-9]{3,15})\/?$", TrainerRedirectorView),
    url(
        r"^u\/(?P<nickname>[A-Za-z0-9]{3,15})\/?$",
        TrainerRedirectorView,
        name="profile_nickname",
    ),
]
