import logging
from typing import Literal, Optional, Union
import requests
from django.conf import settings
from requests.sessions import Session
from urllib.parse import urljoin

from community.discord.constants import AuthTokenType
from community.discord.utils import Snowflake, transform_typed_dict
from community.discord.models import Guild

logger: logging.Logger = logging.Logger(__name__)


class Client:

    GLOBAL_SESSION = requests.Session()
    API_VERSION: int = 9
    API_BASE_URL: str = f"https://discordapp.com/api/v{API_VERSION}"

    def __init__(self, session: Optional[Session] = None) -> None:
        self.session = session or Client.GLOBAL_SESSION

    def auth(
        self,
        token: Optional[str] = None,
        token_type: Literal[AuthTokenType.BOT, AuthTokenType.BEARER] = AuthTokenType.BOT,
    ) -> "Client":
        """Authenticate the client with a token.
        If no values provided, it will attempt to use the token from the settings.
        Returns self for chaining.
        """
        if token is None:
            token = settings.DISCORD_TOKEN
        self.session.headers.update({"Authorization": f"{token_type} {token}"})
        return self

    @property
    def is_authenticated(self) -> bool:
        """Returns True if the client is authenticated."""
        return bool(self.session.headers.get("Authorization"))

    def get(self, url: str, params: dict = None) -> requests.Response:
        """Send a GET request to the specified URL.
        Returns the response.
        """
        return self.session.get(url, params=params)

    def post(self, url: str, data: dict = None) -> requests.Response:
        """Send a POST request to the specified URL.
        Returns the response.
        """
        return self.session.post(url, data=data)

    def get_guild(self, guild_id: Snowflake) -> requests.Response:
        """Get a guild by its ID."""
        url = urljoin(self.API_BASE_URL, f"guilds/{guild_id}")
        params = {"with_counts": True}
        return self.get(url, params=params)

    def get_guild_and_transform(self, guild_id: Snowflake) -> Union[Guild, None]:
        """Get a guild by its ID and transform it into a dict."""
        response = self.get_guild(guild_id)
        dict_ = response.json()
        try:
            response.raise_for_status()
            return transform_typed_dict(dict_, Guild)
        except requests.RequestException as e:
            logger.error("Failed to get guild %s", (guild_id,), exc_info=e)
            return None
