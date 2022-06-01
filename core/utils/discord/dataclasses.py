from typing import TypedDict


class DiscordAuthResponse(TypedDict):
    access_token: str
    token_type: str
    expires_in: int
    scope: str


class PartialGuildObjects(TypedDict):
    id: str
    name: str
    icon: str
    owner: bool
    permissions: str
    features: list[str]
