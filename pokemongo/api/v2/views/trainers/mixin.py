from uuid import UUID
from oauth2_provider.models import AbstractAccessToken, AbstractApplication
from rest_framework.request import Request
from pokemongo.models import Trainer


class CheckTrainerPermissionsMixin:
    def get_trainer_from_uuid(self, uuid: str) -> Trainer:
        """Returns the trainer object for the given uuid."""
        return Trainer.objects.only("uuid", "statistics").get(uuid=uuid)

    def has_permission(
        self,
        request: Request,
        trainer_or_uuid: Trainer | UUID,
        allow_others: bool = True,
    ) -> bool:
        """Controls access to profiles based on the user's permissions."""
        if isinstance(trainer_or_uuid, (UUID, str)):
            trainer = self.get_trainer_from_uuid(trainer_or_uuid)
        elif isinstance(trainer_or_uuid, Trainer):
            trainer = trainer_or_uuid
        else:
            raise TypeError("trainer_or_uuid must be a Trainer or UUID")

        if self.check_if_superuser_client_credentials(request):
            return True
        else:
            return (request.user.trainer.uuid == trainer.uuid) or (
                allow_others and trainer.statistics
            )

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
