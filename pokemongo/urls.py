from django.urls import include, path
from django.views.generic import RedirectView

from pokemongo.views import new_update, leaderboard, profile_redirector

app_name = "trainerdex"

urlpatterns = [
    path(
        "leaderboard/",
        include(
            [
                path("", leaderboard, name="leaderboard"),
                path("country/<str:country>", leaderboard, name="leaderboard"),
                path("community/<slug:community>", leaderboard, name="leaderboard"),
            ]
        ),
    ),
    path("profile/", profile_redirector, name="profile"),
    path("profile/id/<int:id>/", profile_redirector, name="profile"),
    path("new/", new_update, name="update_stats"),
    path(
        "tools/update_stats/",
        RedirectView.as_view(pattern_name="trainerdex:update_stats", permanent=True),
    ),
    path("u/<str:nickname>/", profile_redirector, name="profile"),
    path(
        "",
        RedirectView.as_view(pattern_name="trainerdex:leaderboard", permanent=False),
        name="home",
    ),
]
