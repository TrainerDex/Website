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


"""
URLs for the v2 API.


/api/v2/leaderboard

Do we want seperate endpoints for global and discord leaderboards?
Do we want the diffboard to be a seperate endpoint?
URLs can be a bit long and confusing for these endpoints. Perhaps one endpoint controlled with params?

/api/v2/trainers/@me
/api/v2/trainers/<trainer_name>
/api/v2/trainers/<trainer_name>/nicknames
/api/v2/trainers/<trainer_name>/posts (If we introduce posts)
/api/v2/trainers/<trainer_name>/social
/api/v2/trainers/<trainer_name>/stats
/api/v2/trainers/<trainer_name>/stats/latest


"""
