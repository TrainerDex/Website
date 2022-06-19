from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ModelViewSet

from pokemongo.api.v2.serializers.trainers import UpdateSerializer
from pokemongo.api.v2.views.trainers.mixin import CheckTrainerPermissionsMixin
from pokemongo.models import Update


class UpdateViewSet(ModelViewSet, CheckTrainerPermissionsMixin):
    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ["read"]
    serializer_class = UpdateSerializer
    pagination_class = LimitOffsetPagination

    def get_queryset(self):
        return Update.objects.filter(is_deleted=False, trainer__uuid=self.kwargs["uuid"]).defer(
            "trainer",
            "id",
            "is_deleted",
            "deleted_at",
        )

    def list(self, request, *args, **kwargs):
        if not self.has_permission(request, self.kwargs["uuid"]):
            raise PermissionDenied()
        return super().list(request, *args, **kwargs)
