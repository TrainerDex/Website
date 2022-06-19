from oauth2_provider.contrib.rest_framework import OAuth2Authentication, TokenHasScope
from oauth2_provider.models import AbstractAccessToken, AbstractApplication
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView
from rest_framework.request import Request
from rest_framework.response import Response

from pokemongo.api.v2.serializers.trainers import TrainerDetailSerializer
from pokemongo.models import Trainer


class TrainerDetailView(GenericAPIView):

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

    def has_permission(self, request: Request, trainer: Trainer) -> bool:
        """Controls access to profiles based on the user's permissions."""
        if self.check_if_superuser_client_credentials(request):
            return True
        else:
            return (request.user.trainer.uuid == trainer.uuid) or trainer.statistics

    def check_if_superuser_client_credentials(self, request: Request) -> bool:
        """Checks if the request is made by a superuser-provided confidential client."""
        if (
            isinstance(request.auth, AbstractAccessToken)
            and isinstance(request.auth.application, AbstractApplication)
            and (request.auth.application.client_type == AbstractApplication.CLIENT_CONFIDENTIAL)
            and (
                request.auth.application.authorization_grant_type
                == AbstractApplication.GRANT_CLIENT_CREDENTIALS
            )
            and request.auth.application.user
            and request.auth.application.user.is_superuser
        ):
            return True
        return False

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
