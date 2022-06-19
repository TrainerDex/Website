from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from pokemongo.api.v2.serializers.trainers import NicknameSerializer
from pokemongo.api.v2.views.trainers.mixin import CheckTrainerPermissionsMixin
from pokemongo.models import Nickname


class NicknameViewSet(ModelViewSet, CheckTrainerPermissionsMixin):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ["read"]
    serializer_class = NicknameSerializer

    def get_queryset(self):
        return Nickname.objects.filter(trainer__uuid=self.kwargs["uuid"]).order_by(
            "-active", "nickname"
        )

    def list(self, request, *args, **kwargs):
        if not self.has_permission(request, self.kwargs["uuid"]):
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)
