from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    """
    Hack Permission that gives staff access to everything
    """
    
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS or
                request.user and
                request.user.is_superuser)
