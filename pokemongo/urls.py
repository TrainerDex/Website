# -*- coding: utf-8 -*-
from django.conf.urls import url
from pokemongo.views import LeaderboardHTMLView, TrainerProfileHTMLView, CreateUpdateHTMLView, TrainerRedirectorView

app_name = "trainerdex"

urlpatterns = [
    url(r'^leaderboard\/?$', LeaderboardHTMLView, name='leaderboard'),
    url(r'^leaderboard\/continent\/(?P<continent>[\w]+)\/?$', LeaderboardHTMLView, name='leaderboard'),
    url(r'^leaderboard\/country\/(?P<country>[\w]+)\/?$', LeaderboardHTMLView, name='leaderboard'),
    url(r'^leaderboard\/country\/(?P<country>[\w]+)\/(?P<region>[\w\d]+)\/?$', LeaderboardHTMLView, name='leaderboard'),
    url(r'^leaderboard\/community\/(?P<community>[\w\d]+)\/?$', LeaderboardHTMLView, name='leaderboard'),
    url(r'^profile\/?$', TrainerRedirectorView, name='profile'),
    url(r'^profile\/username\/(?P<username>[\w\d]{3,15})\/?$', TrainerRedirectorView, name='profile'),
    url(r'^profile\/id\/(?P<id>[\d]+)\/?$', TrainerRedirectorView, name='profile'),
    url(r'^tools\/update_stats\/?$', CreateUpdateHTMLView, name='update_stats'),
    url(r'^(?P<username>[A-Za-z0-9]{3,15})\/?$', TrainerRedirectorView),
    url(r'^u\/(?P<username>[A-Za-z0-9]{3,15})\/?$', TrainerProfileHTMLView, name='profile_username'),
]
