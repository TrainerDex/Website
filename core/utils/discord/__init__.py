from __future__ import annotations

from typing import Iterable

import requests
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.discord.provider import DiscordProvider

from core.models.discord import DiscordGuild
from core.utils.discord.auth import DISCORD_BASE_URL
from core.utils.discord.dataclasses import PartialGuildObject


def list_bot_guilds(application: SocialApp) -> list[PartialGuildObject]:
    assert application.provider == DiscordProvider.id

    guilds: list[PartialGuildObject] = []
    has_more: bool = True
    after = None

    # Get guilds for bot user
    headers = {"Authorization": f"Bot {application.key}"}

    while has_more:
        r = requests.get(
            f"{DISCORD_BASE_URL}/users/@me/guilds",
            params={"after": after},
            headers=headers,
        )
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            print(r.text)
            raise e

        if len(data := r.json()) != 200:
            has_more = False
        else:
            after = data[-1]["id"]

        guilds.extend(data)

    return guilds


def upsert_guilds(guilds: Iterable[PartialGuildObject]) -> list[DiscordGuild]:
    return DiscordGuild.objects.bulk_upsert(
        conflict_target=("id",),
        rows=[
            dict(
                id=int(guild["id"]),
                name=guild.get("name"),
                data=guild,
            )
            for guild in guilds
        ],
        return_model=True,
    )


def get_and_insert_bot_guilds(application: SocialApp) -> list[DiscordGuild]:
    guilds: list[PartialGuildObject] = list_bot_guilds(application)
    return upsert_guilds(guilds)
