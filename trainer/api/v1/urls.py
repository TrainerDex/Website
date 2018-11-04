# -*- coding: utf-8 -*-
from django.conf.urls import url
from trainer.api.v1.views import TrainerListJSONView, TrainerDetailJSONView, UpdateListJSONView, LatestUpdateJSONView, UpdateDetailJSONView, UserViewSet, SocialLookupJSONView, LeaderboardJSONView, DiscordLeaderboardAPIView

app_name = "trainerdex.api.1"

urlpatterns = [
    # /leaderboard/
    url(r'^leaderboard\/discord\/(?P<guild>[0-9]+)\/$', DiscordLeaderboardAPIView.as_view()),
    url(r'^leaderboard\/$', LeaderboardJSONView.as_view()),
    # /trainers/
    url(r'^trainers\/$', TrainerListJSONView.as_view()),
    url(r'^trainers\/(?P<pk>[0-9]+)\/$', TrainerDetailJSONView.as_view()),
    url(r'^trainers\/(?P<pk>[0-9]+)\/updates\/$', UpdateListJSONView.as_view()),
    url(r'^trainers\/(?P<pk>[0-9]+)\/updates\/latest\/$', LatestUpdateJSONView.as_view(), name='latest_update'),
    url(r'^trainers\/(?P<pk>[0-9]+)\/updates\/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})\/$', UpdateDetailJSONView.as_view()),
    # /users/
    url(r'^users\/$', UserViewSet.as_view({'get':'list','post':'create'})),
    url(r'^users\/(?P<pk>[0-9]+)\/$', UserViewSet.as_view({'get':'retrieve','patch':'partial_update'})),
    url(r'^users\/social\/$', SocialLookupJSONView.as_view()),
]
