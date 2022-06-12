from django.contrib.auth.models import AbstractBaseUser
from django.db.models import Q
from django.http import HttpRequest
from rest_framework.permissions import BasePermission

from core.models.discord import DiscordGuild


class DiscordGuildPermissions(BasePermission):
    """
    The request is authenticated by checking the user is in a guild.

    This permission can only be applied against view classes that
    provide a `.guild` attribute.
    """

    authenticated_users_only = True

    def check_if_in_guild(self, user: AbstractBaseUser, guild: DiscordGuild) -> bool:
        """
        Given a Guild instance and an HTTP method, return the list of permission
        codes that the user is required to have.
        """
        return user.socialaccount_set.filter(
            Q(guild_memberships__guild=guild) & Q(guild_memberships__active=True)
        ).exists()

    def _guild(self, view) -> DiscordGuild:
        assert hasattr(view, "get_guild") or getattr(view, "guild", None) is not None, (
            "Cannot apply {} on a view that does not set "
            "`.guild` or have a `.get_guild()` method."
        ).format(self.__class__.__name__)

        if hasattr(view, "get_guild"):
            guild = view.get_guild()
            assert guild is not None, "{}.get_guild() returned None".format(
                view.__class__.__name__
            )
            return guild
        return view.guild

    def has_permission(self, request: HttpRequest, view):
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        if not request.user or (
            not request.user.is_authenticated and self.authenticated_users_only
        ):
            return False

        guild = self._guild(view)
        perms = self.check_if_in_guild(request.user, guild.model)

        return perms
