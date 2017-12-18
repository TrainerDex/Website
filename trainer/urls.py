from django.conf.urls import url
from trainer.views import TrainerListView, TrainerDetailView, UpdateListView, UpdateDetailView, TrainerOwnerRedirect, QuickUpdateDialogView
from trainer.errors import ThrowMalformedPKError, ThrowMalformedUUIDError

urlpatterns = [
    url(r'^$', TrainerListView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', TrainerDetailView.as_view()),
    url(r'^(?P<pk>[0-9]+)/updates/$', UpdateListView.as_view()),
    url(r'^(?P<pk>[0-9]+)/updates/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$', UpdateDetailView.as_view()),
    url(r'^(?P<pk>.+)/updates/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$', ThrowMalformedPKError),
    #url(r'^(?P<pk>[0-9]+)/updates/(.+)', ThrowMalformedUUIDError),
    url(r'^(?P<pk>[0-9]+)/owner/$', TrainerOwnerRedirect.as_view()),
    url(r'^tools/update_dialog/$', QuickUpdateDialogView, name='update_dialog'),
]
