from django.conf.urls import url
from trainer.views import TrainerListView, TrainerDetailView, UpdateListView, UpdateDetailView, TrainerOwnerRedirect, QuickUpdateDialogView


urlpatterns = [
    url(r'^$', TrainerListView.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', TrainerDetailView.as_view()),
    url(r'^(?P<pk>[0-9]+)/updates/$', UpdateListView.as_view()),
    url(r'^(?P<pk>[0-9]+)/updates/(?P<uuid>[0-9]+)/$', UpdateDetailView.as_view()),
    url(r'^(?P<pk>[0-9]+)/owner/$', TrainerOwnerRedirect.as_view()),
    url(r'^tools/update_dialog/$', QuickUpdateDialogView, name='update_dialog'),
]
