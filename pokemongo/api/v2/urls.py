from django.urls import path

from pokemongo.api.v2.views.leaderboard import get_global_leaderboard

app_name = "trainerdex.api.2"

urlpatterns = [
    path("leaderboard/", get_global_leaderboard),
]
