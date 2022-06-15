from django.urls import path

from pokemongo.api.v2.views.diffboard import get_discord_diffboard
from pokemongo.api.v2.views.leaderboard import (
    get_discord_leaderboard,
    get_global_leaderboard,
)

app_name = "trainerdex.api.2"

urlpatterns = [
    path("leaderboard/", get_global_leaderboard),
    path("discord-leaderboard/<int:guild_id>/", get_discord_leaderboard),
    path("discord-diffboard/<int:guild_id>/", get_discord_diffboard),
]
