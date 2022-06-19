from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from pokemongo.api.v2.serializers.trainers import TrainerDetailSerializer
from pokemongo.api.v2.views.trainers.mixin import CheckTrainerPermissionsMixin
from pokemongo.models import Trainer


class TrainerDetailView(GenericAPIView, CheckTrainerPermissionsMixin):

    authentication_classes = [OAuth2Authentication]
    permission_classes = [TokenHasScope]
    required_scopes = ["read"]
    serializer_class = TrainerDetailSerializer

    queryset = Trainer.objects.filter(owner__is_active=True).only(
        "uuid",
        "created_at",
        "updated_at",
        "_nickname",
        "start_date",
        "faction",
        "trainer_code",
        "verified",
        "statistics",
        "last_cheated",
    )
    lookup_field = "uuid"

    def get(self, request: Request, *args, **kwargs):
        if self.kwargs.get(self.lookup_field) is None:
            if request.user:
                self.kwargs[self.lookup_field] = request.user.trainer.uuid
            else:
                raise PermissionDenied()

        trainer: Trainer = self.get_object()

        if not self.has_permission(request, trainer):
            raise PermissionDenied()

        return Response(self.get_serializer(trainer).data)
