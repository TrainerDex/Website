from typing import Iterable
import requests
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.discord.provider import DiscordProvider

from core.models.discord import DiscordGuild
from core.utils.discord.auth import authenticate, DISCORD_BASE_URL
from core.utils.discord.dataclasses import DiscordAuthResponse, PartialGuildObjects


def list_bot_guilds(application: SocialApp) -> list[PartialGuildObjects]:
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


def upsert_guilds(guilds: Iterable[PartialGuildObjects]) -> list[DiscordGuild]:
    return DiscordGuild.objects.bulk_upsert(
        conflict_target="id",
        rows=[
            dict(
                id=int(guild["id"]),
                name=guild["name"],
                owner_id=guild["owner"],
                data=guild,
            )
            for guild in guilds
        ],
        return_model=True,
    )


def get_and_insert_bot_guilds(application: SocialApp) -> list[DiscordGuild]:
    guilds: list[PartialGuildObjects] = list_bot_guilds(application)
    return upsert_guilds(guilds)
