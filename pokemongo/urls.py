# -*- coding: utf-8 -*-
from django.conf.urls import url
from pokemongo.views import LeaderboardHTMLView, TrainerProfileHTMLView, CreateUpdateHTMLView, TrainerRedirectorView

app_name = "trainerdex"

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
]
