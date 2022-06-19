from allauth.socialaccount.models import SocialAccount
from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet

from pokemongo.api.v2.serializers.trainers import SocialAccountSerializer
from pokemongo.api.v2.views.trainers.mixin import CheckTrainerPermissionsMixin


class SocialAccountViewSet(ModelViewSet, CheckTrainerPermissionsMixin):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ["read:social"]
    serializer_class = SocialAccountSerializer

    def get_queryset(self):
        return SocialAccount.objects.filter(user__trainer__uuid=self.kwargs["uuid"])

    def list(self, request, *args, **kwargs):
        if not self.has_permission(request, self.kwargs["uuid"]):
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)
