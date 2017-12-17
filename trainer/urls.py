from django.conf.urls import url
from trainer.views import TrainerListView, TrainerDetailView, UpdateListView, UpdateDetailView, TrainerOwnerRedirect, QuickUpdateDialogView


urlpatterns = [
    url(r'^$', TrainerListView.as_view()),
    url(r'^<int:id>/$', TrainerDetailView.as_view()),
    url(r'^<int:trainer>/updates/$', UpdateListView.as_view()),
    url(r'^<int:trainer>/updates/<int:uuid>/$', UpdateDetailView.as_view()),
    url(r'^<int:id>/owner/$', TrainerOwnerRedirect.as_view()),
    url(r'^tools/update_dialog/$', QuickUpdateDialogView, name='update_dialog'),
]
