from django.conf.urls import url
from django.views.generic import RedirectView
from pokemongo.views import LeaderboardView, CreateUpdateView, TrainerRedirectorView

app_name = "trainerdex"

urlpatterns = [
    url(r"^leaderboard\/?$", LeaderboardView, name="leaderboard"),
    url(r"^leaderboard\/country\/(?P<country>[\w]+)\/?$", LeaderboardView, name="leaderboard"),
    url(
        r"^leaderboard\/community\/(?P<community>[\w\d]+)\/?$",
        LeaderboardView,
        name="leaderboard",
    ),
    url(r"^profile\/?$", TrainerRedirectorView, name="profile"),
    url(r"^profile\/id\/(?P<id>[\d]+)\/?$", TrainerRedirectorView, name="profile"),
    url(r"^new\/?$", CreateUpdateView, name="update_stats"),
    url(r"^tools\/update_stats\/?$", RedirectView.as_view(url="update_stats", permanent=True)),
    url(r"^(?P<nickname>[A-Za-z0-9]{3,15})\/?$", TrainerRedirectorView),
    url(
        r"^u\/(?P<nickname>[A-Za-z0-9]{3,15})\/?$", TrainerRedirectorView, name="profile_nickname",
    ),
]
