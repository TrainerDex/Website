from oauth2_provider.contrib.rest_framework import OAuth2Authentication
from rest_framework.viewsets import ModelViewSet

from core.api.serializers import DiscordPreferencesSerializer
from core.models.discord import DiscordGuild
from core.permissions.legacy import IsStaff


class DiscordPreferencesView(ModelViewSet):
    queryset = (
        DiscordGuild.objects.select_related(
            "mystic_role",
            "valor_role",
            "instinct_role",
            "tl40_role",
            "tl50_role",
            "leaderboard_channel",
        )
        .prefetch_related(
            "mod_role_ids",
            "roles_to_append_on_approval",
            "roles_to_remove_on_approval",
        )
        .defer(
            "data",
            "cached_date",
            "has_access",
            "owner_id",
        )
    )
    authentication_classes = [OAuth2Authentication]
    serializer_class = DiscordPreferencesSerializer
    permission_classes = [IsStaff]
