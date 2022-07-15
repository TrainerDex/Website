from django.urls import path

from pokemongo.api.v2.views import LeaderboardViewFinder

app_name = "trainerdex.api.2"

urlpatterns = [
    path("leaderboard/", LeaderboardViewFinder.as_view()),
]


"""
URLs for the v2 API.


/api/v2/leaderboard

/api/v2/trainers/@me
/api/v2/trainers/<trainer_name>
/api/v2/trainers/<trainer_name>/nicknames
/api/v2/trainers/<trainer_name>/posts (If we introduce posts)
/api/v2/trainers/<trainer_name>/social
/api/v2/trainers/<trainer_name>/stats
/api/v2/trainers/<trainer_name>/stats/latest


"""
