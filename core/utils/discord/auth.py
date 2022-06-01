import requests

from core.utils.discord.dataclasses import DiscordAuthResponse


DISCORD_BASE_URL = "https://discordapp.com/api/v9"


def authenticate(client_id: str, secret: str) -> DiscordAuthResponse:
    data = {"grant_type": "client_credentials", "scope": "identify guilds"}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(
        f"{DISCORD_BASE_URL}/oauth2/token",
        data=data,
        headers=headers,
        auth=(client_id, secret),
    )
    r.raise_for_status()
    return r.json()
