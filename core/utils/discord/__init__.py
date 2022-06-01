from typing import Iterable
import requests
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.discord.provider import DiscordProvider

from core.models.discord import DiscordGuild
from core.utils.discord.auth import authenticate, DISCORD_BASE_URL
from core.utils.discord.dataclasses import DiscordAuthResponse, PartialGuildObjects


def list_guilds(application: SocialApp) -> list[PartialGuildObjects]:
    assert application.provider == DiscordProvider.id

    # Authenticate
    bearer_token: DiscordAuthResponse = authenticate(application.client_id, application.secret)

    guilds: list[PartialGuildObjects] = []
    has_more: bool = True
    after = None

    # Get guilds for bot user
    headers = {"Authorization": f"Bearer {bearer_token['access_token']}"}

    while has_more:
        r = requests.get(
            f"{DISCORD_BASE_URL}/users/@me/guilds",
            params={"after": after},
            headers=headers,
        )
        r.raise_for_status()

        if len(data := r.json()) != 200:
            has_more = False
        else:
            after = data[-1]["id"]

        guilds.extend(data)

    return guilds


def ingest_guilds(guilds: Iterable[PartialGuildObjects]):
    for guild in guilds:
        DiscordGuild.objects.update_or_create(
            id=int(guild["id"]),
            defaults=dict(
                name=guild["name"],
                owner_id=guild["owner"],
                data=guild,
            ),
        )
