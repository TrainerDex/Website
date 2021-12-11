from typing import Any

from django.http import HttpRequest
from rest_framework import permissions


class IsStaffUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request: HttpRequest, _) -> bool:
        return request.method in permissions.SAFE_METHODS or request.user and request.user.is_staff
