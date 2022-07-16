from django.urls import path

from pokemongo.views import home, leaderboard, new_update, profile_redirector

app_name = "trainerdex"

urlpatterns = [
    path("leaderboard", leaderboard, name="leaderboard"),
    path("profile/", profile_redirector, name="profile"),
    path("profile/id/<int:id>/", profile_redirector, name="profile"),
    path("new/", new_update, name="update_stats"),
    path("u/<str:nickname>/", profile_redirector, name="profile"),
    path("", home, name="home"),
]
