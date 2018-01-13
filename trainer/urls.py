from django.conf.urls import url
from trainer.views import TrainerListJSONView, TrainerDetailJSONView, UpdateListJSONView, LatestUpdateJSONView, UpdateDetailJSONView, UserViewSet, SocialLookupJSONView
from trainer.errors import ThrowMalformedPKError, ThrowMalformedUUIDError

class TrainerURLs:
    
    urlpatterns = [
        url(r'^$', TrainerListJSONView.as_view()),
        url(r'^(?P<pk>[0-9]+)/$', TrainerDetailJSONView.as_view()),
        url(r'^(?P<pk>[0-9]+)/updates/$', UpdateListJSONView.as_view()),
        url(r'^(?P<pk>[0-9]+)/updates/latest/$', LatestUpdateJSONView.as_view()),
        url(r'^(?P<pk>[0-9]+)/updates/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$', UpdateDetailJSONView.as_view()),
        url(r'^(?P<pk>.+)/updates/(?P<uuid>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$', ThrowMalformedPKError),
        #url(r'^(?P<pk>[0-9]+)/updates/(.+)', ThrowMalformedUUIDError),
    ]

class UserURLs:
    
    urlpatterns = [
        url(r'^$', UserViewSet.as_view({'get':'list','post':'create'})),
        url(r'^(?P<pk>[0-9]+)/$', UserViewSet.as_view({'get':'retrieve','patch':'partial_update'})),
        url(r'^social/$', SocialLookupJSONView.as_view()),
    ]