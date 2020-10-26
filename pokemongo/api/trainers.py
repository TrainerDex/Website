from django.urls import include, path

from djangorestversioning.versioning import VersionedEndpoint
from rest_framework.views import APIView

class TrainerListView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.trainers.TrainerListView",
    }

class TrainerDetailView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.trainers.TrainerDetailView",
    }

class UpdateListView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.trainers.UpdateListView",
    }

class LatestUpdateView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.trainers.LatestUpdateView",
        2.0: "pokemongo.api.v2.trainers.LatestUpdateRedirector",
    }

class UpdateDetailView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.trainers.UpdateDetailView",
    }


urlpatterns = [
    path("", TrainerListView.as_view(), name="trainer-list"),
    path(
        "<int:pk>/",
        include(
            [
                path("", TrainerDetailView.as_view(), name="trainer-detail"),
                path("updates/", UpdateListView.as_view(), name="trainer-update-list"),
                path("updates/latest/", LatestUpdateView.as_view(), name="trainer-update-latest"),
                path("updates/<uuid:uuid>/", UpdateDetailView.as_view(), name="trainer-update-detail"),
            ]
        ),
    ),
]
