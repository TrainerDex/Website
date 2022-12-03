from typing import Union

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser, AbstractUser
from oauth2_provider.models import AbstractAccessToken, AbstractApplication
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request


class IsStaff(BasePermission):
    """
    Allows access only to admin users.
    """

    @staticmethod
    def user_is_staff(user: Union[AbstractBaseUser, AnonymousUser, None]) -> bool:
        return isinstance(user, AbstractUser) and user.is_staff

    @staticmethod
    def get_user_from_oauth2_request(
        request: Request,
    ) -> Union[AbstractBaseUser, None]:
        if isinstance(request.auth, AbstractAccessToken) and isinstance(
            request.auth.application, AbstractApplication
        ):
            if request.auth.application.client_type == AbstractApplication.CLIENT_CONFIDENTIAL:
                if request.auth.application.authorization_grant_type in {
                    AbstractApplication.GRANT_PASSWORD,
                    AbstractApplication.GRANT_CLIENT_CREDENTIALS,
                }:
                    return request.auth.application.user

        return None

    def has_permission(self, request: Request, view):
        return self.user_is_staff(request.user) or self.user_is_staff(
            self.get_user_from_oauth2_request(request)
        )


class IsStaffOrReadOnly(IsStaff):
    def has_permission(self, request: Request, view) -> bool:
        is_staff = super().has_permission(request, view)
        return is_staff or request._request.method in SAFE_METHODS
