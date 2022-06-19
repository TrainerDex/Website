from django.urls import path

from pokemongo.api.v2.views import (
    LeaderboardViewFinder,
    NicknameViewSet,
    TrainerDetailView,
    SocialAccountViewSet,
)

app_name = "trainerdex.api.2"

urlpatterns = [
    path("leaderboard/", LeaderboardViewFinder.as_view()),
    path("trainers/@me/", TrainerDetailView.as_view()),
    path("trainers/<uuid:uuid>/", TrainerDetailView.as_view()),
    path("trainers/<uuid:uuid>/nicknames/", NicknameViewSet.as_view({"get": "list"})),
    path("trainers/<uuid:uuid>/social/", SocialAccountViewSet.as_view({"get": "list"})),
]


"""
URLs for the v2 API.


/api/v2/leaderboard

/api/v2/trainers/@me
/api/v2/trainers/<uuid:uuid>
/api/v2/trainers/<uuid:uuid>/nicknames
/api/v2/trainers/<uuid:uuid>/posts (If we introduce posts)
/api/v2/trainers/<uuid:uuid>/social
/api/v2/trainers/<uuid:uuid>/stats
/api/v2/trainers/<uuid:uuid>/stats/latest


"""
