from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.contrib.rest_framework.permissions import (
    TokenHasScope,
    TokenMatchesOASRequirements,
)
from rest_framework.request import Request
from rest_framework.permissions import BasePermission, IsAdminUser

from core.permissions.legacy import IsStaffOrReadOnly


class IsStaffOrReadOnlyOrTokenHasScope(BasePermission):
    def has_permission(self, request: Request, view):
        is_authenticated = IsStaffOrReadOnly().has_permission(request, view)
        oauth2authenticated = False
        if is_authenticated:
            oauth2authenticated = isinstance(
                request.successful_authenticator, OAuth2Authentication
            )

        token_has_scope = TokenHasScope()
        return (is_authenticated and not oauth2authenticated) or token_has_scope.has_permission(
            request, view
        )


class IsStaffOrTokenHasScope(BasePermission):
    def has_permission(self, request: Request, view):
        is_authenticated = IsAdminUser().has_permission(request, view)
        oauth2authenticated = False
        if is_authenticated:
            oauth2authenticated = isinstance(
                request.successful_authenticator, OAuth2Authentication
            )

        token_has_scope = TokenHasScope()
        return (is_authenticated and not oauth2authenticated) or token_has_scope.has_permission(
            request, view
        )


class IsStaffOrTokenMatchesOASRequirements(BasePermission):
    def has_permission(self, request: Request, view):
        is_authenticated = IsAdminUser().has_permission(request, view)
        oauth2authenticated = False
        if is_authenticated:
            oauth2authenticated = isinstance(
                request.successful_authenticator, OAuth2Authentication
            )

        token_has_scope = TokenMatchesOASRequirements()
        return (is_authenticated and not oauth2authenticated) or token_has_scope.has_permission(
            request, view
        )


class IsStaffOrReadOnlyTokenMatchesOASRequirements(BasePermission):
    def has_permission(self, request: Request, view):
        is_authenticated = IsStaffOrReadOnly().has_permission(request, view)
        oauth2authenticated = False
        if is_authenticated:
            oauth2authenticated = isinstance(
                request.successful_authenticator, OAuth2Authentication
            )

        token_has_scope = TokenMatchesOASRequirements()
        return (is_authenticated and not oauth2authenticated) or token_has_scope.has_permission(
            request, view
        )
