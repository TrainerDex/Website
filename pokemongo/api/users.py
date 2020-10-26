from django.urls import include, path

from djangorestversioning.versioning import VersionedEndpoint
from pokemongo.api.v1.users import UserViewSet
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

class SocialLookupView(VersionedEndpoint, APIView):
    versions = {
        1.0: "pokemongo.api.v1.users.SocialLookupView",
    }


urlpatterns = [
    path("", UserViewSet.as_view({"get": "list", "post": "create"})),
    path("<int:pk>/", UserViewSet.as_view({"get": "retrieve", "patch": "partial_update"})),
    path("social/", SocialLookupView.as_view()),
]
