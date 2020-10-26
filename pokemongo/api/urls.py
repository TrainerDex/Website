from django.urls import include, path

app_name = "api"

urlpatterns = [
    path("leaderboard/", include("pokemongo.api.leaderboard")),
    path("trainers/", include("pokemongo.api.trainers")),
    path("users/", include("pokemongo.api.users")),
]
