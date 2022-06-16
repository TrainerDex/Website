from django.urls import path

from pokemongo.api.v2.views.leaderboard.interface import LeaderboardView


app_name = "trainerdex.api.2"

urlpatterns = [
    path("leaderboard/", LeaderboardView.as_view()),
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
