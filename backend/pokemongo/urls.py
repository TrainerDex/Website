from django.urls import include, path
from django.views.generic import RedirectView, TemplateView

from pokemongo.views import new_update, profile_redirector

app_name = "trainerdex"

urlpatterns = [
    path(
        "leaderboard",
        TemplateView.as_view(
            template_name="leaderboard.html",
        ),
        name="leaderboard",
    ),
    path("profile/", profile_redirector, name="profile"),
    path("profile/id/<int:id>/", profile_redirector, name="profile"),
    path("new/", new_update, name="update_stats"),
    path("u/<str:nickname>/", profile_redirector, name="profile"),
    path(
        "",
        RedirectView.as_view(pattern_name="trainerdex:leaderboard", permanent=False),
        name="home",
    ),
]
