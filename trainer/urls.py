# -*- coding: utf-8 -*-
from django.conf.urls import url
from trainer.views import TrainerListJSONView, TrainerDetailJSONView, UpdateListJSONView, LatestUpdateJSONView, UpdateDetailJSONView, UserViewSet, SocialLookupJSONView, LeaderboardJSONView, DiscordLeaderboardAPIView
from trainer.views import LeaderboardHTMLView, TrainerProfileHTMLView, CreateUpdateHTMLView, UpdateInstanceHTMLView, TrainerRedirectorView, fortyx
from trainer.errors import ThrowMalformedPKError, ThrowMalformedUUIDError
from django.views import defaults
from ekpogo.views import *

class REST:
    
    urlpatterns = [
        # /
        url(r'^leaderboard\/discord\/(?P<guild>[0-9]+)\/$', DiscordLeaderboardAPIView.as_view()),
        url(r'^leaderboard\/$', LeaderboardJSONView.as_view()),
        # /trainers/
        url(r'^trainers\/$', TrainerListJSONView.as_view()),
        url(r'^trainers\/(?P<pk>[0-9]+)\/$', TrainerDetailJSONView.as_view()),
        url(r'^trainers\/(?P<pk>[0-9]+)\/updates\/$', UpdateListJSONView.as_view()),
        url(r'^trainers\/(?P<pk>[0-9]+)\/updates\/latest\/$', LatestUpdateJSONView.as_view()),
        url(r'^trainers\/(?P<pk>[0-9]+)\/updates\/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})\/$', UpdateDetailJSONView.as_view()),
        # /users/
        url(r'^users\/$', UserViewSet.as_view({'get':'list','post':'create'})),
        url(r'^users\/(?P<pk>[0-9]+)\/$', UserViewSet.as_view({'get':'retrieve','patch':'partial_update'})),
        url(r'^users\/social\/$', SocialLookupJSONView.as_view()),
    ]

class HTML:
    
    urlpatterns = [
        url(r'^leaderboard\/?$', LeaderboardHTMLView, name='leaderboard'),
        url(r'^leaderboard\/continent\/(?P<continent>[a-zA-Z]+)\/?$', LeaderboardHTMLView, name='leaderboard'),
        url(r'^leaderboard\/country\/(?P<country>[a-zA-Z]+)\/?$', LeaderboardHTMLView, name='leaderboard'),
        url(r'^leaderboard\/country\/(?P<country>[a-zA-Z]+)\/(?P<region>[a-zA-Z0-9]+)\/?$', LeaderboardHTMLView, name='leaderboard'),
        url(r'^profile\/?$', TrainerRedirectorView, name='profile'),
        url(r'^profile\/username\/(?P<username>[A-Za-z0-9]{3,15})\/?$', TrainerRedirectorView, name='profile'),
        url(r'^profile\/id\/(?P<id>[0-9]+)\/?$', TrainerRedirectorView, name='profile'),
        url(r'^tools\/update_stats\/?$', CreateUpdateHTMLView, name='update_stats'),
        url(r'^(?P<username>[A-Za-z0-9]{3,15})\/?$', TrainerRedirectorView),
        url(r'^u\/(?P<username>[A-Za-z0-9]{3,15})\/?$', TrainerProfileHTMLView, name='profile_username'),
        url(r'^update\/([a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})\/?$', Raise404UpdateURL),
        url(r'^u\/(?P<username>[A-Za-z0-9]{3,15})\/40x?$', fortyx, name='profile_40x'),
    ]
