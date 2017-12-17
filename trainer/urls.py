from django.conf.urls import url
from trainer.views import TrainerListView, TrainerDetailView, UpdateListView, UpdateDetailView, TrainerOwnerRedirect


urlpatterns = [
    url(r'^trainers/', TrainerListView),
    url(r'^trainers/<int:id>', TrainerDetailView),
    url(r'^trainers/<int:trainer>/updates/', UpdateListView),
    url(r'^trainers/<int:trainer>/updates/<int:uuid>/', UpdateDetailView),
    url(r'^trainers/<int:id>/owner', TrainerOwnerRedirect),
]
