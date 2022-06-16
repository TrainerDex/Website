from django.http import HttpRequest
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request: HttpRequest, view) -> bool:
        return (request.method in SAFE_METHODS) or (request.user and request.user.is_staff)
