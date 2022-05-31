from typing import Any

from django.http import HttpRequest
from oauth2_provider.contrib.rest_framework.authentication import OAuth2Authentication
from oauth2_provider.contrib.rest_framework.permissions import (
    TokenHasScope,
    TokenMatchesOASRequirements,
)
from rest_framework.permissions import SAFE_METHODS, BasePermission, IsAdminUser


class IsAdminUserOrReadOnly(BasePermission):
    def has_permission(self, request: HttpRequest, view: Any) -> bool:
        return request.method in SAFE_METHODS or request.user and request.user.is_staff


class IsAdminUserOrReadOnlyOrTokenHasScope(BasePermission):
    def has_permission(self, request: HttpRequest, view):
        is_authenticated = IsAdminUserOrReadOnly().has_permission(request, view)
        oauth2authenticated = False
        if is_authenticated:
            oauth2authenticated = isinstance(
                request.successful_authenticator, OAuth2Authentication
            )

        token_has_scope = TokenHasScope()
        return (is_authenticated and not oauth2authenticated) or token_has_scope.has_permission(
            request, view
        )


class IsAdminUserOrTokenHasScope(BasePermission):
    def has_permission(self, request: HttpRequest, view):
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


class IsAdminUserOrTokenMatchesOASRequirements(BasePermission):
    def has_permission(self, request, view):
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


class IsAdminUserOrReadOnlyOrTokenHasScope(BasePermission):
    def has_permission(self, request, view):
        is_authenticated = IsAdminUserOrReadOnly().has_permission(request, view)
        oauth2authenticated = False
        if is_authenticated:
            oauth2authenticated = isinstance(
                request.successful_authenticator, OAuth2Authentication
            )

        token_has_scope = TokenMatchesOASRequirements()
        return (is_authenticated and not oauth2authenticated) or token_has_scope.has_permission(
            request, view
        )
