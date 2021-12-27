import datetime
import logging
from django.db.models.utils import resolve_callables
from django.db.utils import IntegrityError
import pytz
import requests
from requests.models import Response
from typing import Dict, List, Optional, Tuple, TypedDict, Union

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from simple_history.models import HistoricalRecords

from community.discord.constants import (
    IMAGE_BASE_URL,
    PREFERED_ANIMATED_IMAGE_FORMATS,
    PREFERED_STILL_IMAGE_FORMATS,
)
from community.discord.enums import (
    UserFlags,
    PremiumTypes,
    VerificationLevel,
    DefaultMessageNotifications,
    ExplicitContentFilterLevel,
    MFALevel,
    SystemChannelFlags,
    ChannelTypes,
    OverwriteType,
    Permissions,
    VideoQualityModes,
    ActivityTypes,
    ActivityFlags,
    PresenceStatus,
    PremiumTier,
    GuildNSFWLevel,
    StagePrivacyLevel,
    StickerType,
    StickerFormat,
    ScheduledEventPrivacyLevel,
    ScheduledEventStatus,
    ScheduledEventEntityType,
)
from community.discord.utils import Snowflake, get_best_file_format, transform_typed_dict
from community.models import BaseCommunity

logger: logging.Logger = logging.getLogger(__name__)


class RoleTags(TypedDict, total=False):
    bot_id: Snowflake
    intergration_id: Snowflake
    premium_subscriber: None


class Role(TypedDict, total=False):
    id: Snowflake
    name: str
    color: int
    hoist: bool
    icon: Optional[str]
    unicode_emoji: Optional[str]
    position: int
    permissions: str
    managed: bool
    mentionable: bool
    tags: RoleTags


class User(TypedDict, total=False):
    id: Snowflake
    username: str
    discriminator: str
    avatar: Optional[str]
    bot: bool
    system: bool
    mfa_enabled: bool
    banner: Optional[str]
    accent_color: Optional[int]
    locale: str
    verified: bool
    email: Optional[str]
    flags: UserFlags
    premium_type: Optional[PremiumTypes]
    public_flags: UserFlags


class Emoji(TypedDict, total=False):
    id: Optional[Snowflake]
    name: Optional[str]
    roles: List[Role]
    user: Optional[User]
    require_colons: bool
    managed: bool
    animated: bool
    available: bool


class GuildMember(TypedDict, total=False):
    user: User
    nick: Optional[str]
    avatar: Optional[str]
    roles: List[Snowflake]
    joined_at: datetime.datetime
    premium_since: Optional[datetime.datetime]
    deaf: bool
    mute: bool
    pending: bool
    permissions: str
    communication_disabled_until: Optional[datetime.datetime]


class VoiceState(TypedDict, total=False):
    guild_id: Snowflake
    channel_id: Optional[Snowflake]
    user_id: Snowflake
    member: GuildMember
    session_id: str
    deaf: bool
    mute: bool
    self_deaf: bool
    self_mute: bool
    suppress: bool
    self_stream: Optional[bool]
    self_video: bool
    suppress: bool
    request_to_speak_timestamp: datetime.datetime


class Overwrite(TypedDict, total=False):
    id: Snowflake
    type: OverwriteType
    allow: Permissions
    deny: Permissions


class ThreadMetadata(TypedDict, total=False):
    archived: bool
    auto_archive_duration: int
    archive_timestamp: datetime.datetime
    locked: bool
    invitable: bool


class ThreadMember(TypedDict, total=False):
    id: Snowflake
    user_id: Snowflake
    join_timestamp: datetime.datetime
    flags: int


class Channel(TypedDict, total=False):
    id: Snowflake
    type: ChannelTypes
    guild_id: Snowflake
    position: int
    permission_overwrites: List[Overwrite]
    name: str
    topic: Optional[str]
    nsfw: bool
    last_message_id: Optional[Snowflake]
    bitrate: int
    user_limit: int
    rate_limit_per_user: int
    recipients: List[User]
    icon: Optional[str]
    owner_id: Snowflake
    application_id: Snowflake
    parent_id: Optional[Snowflake]
    last_pin_timestamp: Optional[datetime.datetime]
    rtc_region: Optional[str]
    video_quality_mode: VideoQualityModes
    message_count: int
    member_count: int
    thread_metadata: ThreadMetadata
    member: ThreadMember
    default_auto_archive_duration: int
    permissions: Permissions


class ActivityTimestamps(TypedDict, total=False):
    start: datetime.datetime
    end: datetime.datetime


class ActivityEmoji(TypedDict, total=False):
    name: str
    id: Snowflake
    animated: bool


class ActivityParty(TypedDict, total=False):
    id: str
    size: Tuple[int, int]


class ActivityAssets(TypedDict, total=False):
    large_image: str
    large_text: str
    small_image: str
    small_text: str


class ActivitySecrets(TypedDict, total=False):
    join: str
    spectate: str
    match: str


class ActivityButton(TypedDict, total=False):
    label: str
    url: str


class Activity(TypedDict, total=False):
    name: str
    type: ActivityTypes
    url: Optional[str]
    created_at: datetime.datetime
    timestamps: ActivityTimestamps
    application_id: Snowflake
    details: str
    state: str
    emoji: Optional[ActivityEmoji]
    party: ActivityParty
    assets: ActivityAssets
    secrets: ActivitySecrets
    instance: bool
    flags: ActivityFlags
    buttons: List[ActivityButton]


class ClientStatus(TypedDict, total=False):
    desktop: PresenceStatus
    mobile: PresenceStatus
    web: PresenceStatus


class PresenceUpdate(TypedDict, total=False):
    user: User
    guild_id: Snowflake
    status: PresenceStatus
    activities: List[Activity]
    client_status: ClientStatus


class WelcomeScreenChannel(TypedDict, total=False):
    channel_id: Snowflake
    description: str
    emoji_id: Optional[Snowflake]
    emoji_name: Optional[str]


class WelcomeScreen(TypedDict, total=False):
    description: str
    welcome_channels: List[WelcomeScreenChannel]


class StageInstance(TypedDict, total=False):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    topic: str
    privacy_level: StagePrivacyLevel
    discoverable_disabled: bool


class Sticker(TypedDict, total=False):
    id: Snowflake
    pack_id: Snowflake
    name: str
    description: Optional[str]
    tags: str
    asset: str
    type: StickerType
    format_type: StickerFormat
    available: bool
    guild_id: Snowflake
    user: User
    sort_value: int


class ScheduledEventEntityMetadata(TypedDict):
    location: str


class ScheduledEvent(TypedDict, total=False):
    id: Snowflake
    guild_id: Snowflake
    channel_id: Snowflake
    creator_id: Snowflake
    name: str
    description: Optional[str]
    scheduled_start_time: datetime.datetime
    scheduled_end_time: Optional[datetime.datetime]
    privacy_level: ScheduledEventPrivacyLevel
    status: ScheduledEventStatus
    entity_type: ScheduledEventEntityType
    entity_id: Optional[Snowflake]
    entity_metadata: Optional[ScheduledEventEntityMetadata]
    creator: User
    user_count: int


class Guild(TypedDict, total=False):
    id: Snowflake
    name: str
    icon: Optional[str]
    icon_hash: Optional[str]
    splash: Optional[str]
    discovery_splash: Optional[str]
    owner: Optional[bool]
    owner_id: Snowflake
    permissions: str
    region: Optional[str]
    afk_channel_id: Optional[Snowflake]
    afk_timeout: int
    widget_enabled: bool
    widget_channel_id: Optional[Snowflake]
    verification_level: VerificationLevel
    default_message_notifications: DefaultMessageNotifications
    explicit_content_filter: ExplicitContentFilterLevel
    roles: List[Role]
    emojis: List[Emoji]
    features: List[str]
    mfa_level: MFALevel
    application_id: Optional[Snowflake]
    system_channel_id: Optional[Snowflake]
    system_channel_flags: SystemChannelFlags
    rules_channel_id: Optional[Snowflake]
    joined_at: datetime.datetime
    large: bool
    unavailable: bool
    member_count: int
    voice_states: List[VoiceState]
    members: List[GuildMember]
    channels: List[Channel]
    threads: List[Channel]
    presences: List[PresenceUpdate]
    max_presences: Optional[int]
    max_members: int
    vanity_url_code: Optional[str]
    description: Optional[str]
    banner: Optional[str]
    premium_tier: PremiumTier
    premium_subscription_count: int
    preferred_locale: str
    public_updates_channel_id: Optional[Snowflake]
    max_video_channel_users: int
    approximate_member_count: int
    approximate_presence_count: int
    welcome_screen: WelcomeScreen
    nsfw_level: GuildNSFWLevel
    stage_instances: List[StageInstance]
    stickers: List[Sticker]
    guild_scheduled_events: List[ScheduledEvent]
    premium_progress_bar_enabled: bool


class DiscordCommunityQuerySet(models.QuerySet):
    def create(self, from_api: bool = True, **kwargs) -> "DiscordCommunity":
        """
        Create a new object with the given kwargs, saving it to the database
        and returning the created object.
        """
        obj: "DiscordCommunity" = self.model(**kwargs)
        self._for_write = True
        if from_api:
            obj.get_details_from_api()
        obj.save(force_insert=True, using=self.db)
        return obj

    def get_or_create(self, defaults=None, from_api: bool = True, **kwargs):
        """
        Look up an object with the given kwargs, creating one if necessary.
        Return a tuple of (object, created), where created is a boolean
        specifying whether an object was created.
        """
        # The get() needs to be targeted at the write database in order
        # to avoid potential transaction consistency problems.
        self._for_write = True
        try:
            return self.get(**kwargs), False
        except self.model.DoesNotExist:
            params = self._extract_model_params(defaults, **kwargs)
            # Try to create an object using passed params.
            try:
                with transaction.atomic(using=self.db):
                    params = dict(resolve_callables(params))
                    return self.create(from_api, **params), True
            except IntegrityError:
                try:
                    return self.get(**kwargs), False
                except self.model.DoesNotExist:
                    pass
                raise

    def update_or_create(self, defaults=None, from_api: bool = True, **kwargs):
        """
        Look up an object with the given kwargs, updating one with defaults
        if it exists, otherwise create a new one.
        Return a tuple (object, created), where created is a boolean
        specifying whether an object was created.
        """
        defaults = defaults or {}
        self._for_write = True
        with transaction.atomic(using=self.db):
            # Lock the row so that a concurrent update is blocked until
            # update_or_create() has performed its save.
            obj, created = self.select_for_update().get_or_create(defaults, from_api, **kwargs)
            if created:
                return obj, created
            for k, v in resolve_callables(defaults):
                setattr(obj, k, v)
            if from_api:
                obj.get_details_from_api()
            obj.save(using=self.db)
        return obj, False


class DiscordCommunityManager(models.Manager):
    def get_queryset(self) -> models.QuerySet["DiscordCommunity"]:
        return DiscordCommunityQuerySet(self.model, using=self._db)


class DiscordCommunity(BaseCommunity):
    """This is a data model which will take a Discord Guild object from the Discord API and cache it's data."""

    preferred_locale = models.CharField(
        default="en-US",
        max_length=50,
        verbose_name=_("Language"),
        help_text=_(
            "The primary language of the community. This is used for all communications and leaderboard positions."
        ),
    )
    preferred_timezone = models.CharField(
        max_length=len(max(pytz.common_timezones, key=len)),
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default="UTC",
        verbose_name=_("Timezone"),
        help_text=_(
            "The primary timezone of the community. This is used for all communications and leaderboard positions."
        ),
    )

    # Track the history of this object
    history = HistoricalRecords()

    # Custom manager for searching and creating objects
    objects = DiscordCommunityManager()

    # Store the Discord Guild object
    # We're storing this as a JSONb field because the Discord API changes the format without much warning.
    # In pre-save, we will explode out fields we care about.
    details: Guild = models.JSONField(null=False, blank=True, default=dict)

    def set_details(self, details: Dict) -> "DiscordCommunity":
        # Transform dictionary values based on TypedDict definitions
        self.details: Guild = transform_typed_dict(details, Guild)

        # Warn if any fields in details aren't in the Guild annotation
        for k, v in details.items():
            if k not in Guild.__annotations__:
                logger.warn("Unknown field %s in Guild object", k)
        return self

    # Exploded fields, all with editable=False as they are not expected to be changed manually.
    id = models.PositiveBigIntegerField(
        primary_key=True,
        editable=False,
        help_text="guild id",
    )
    name = models.CharField(
        max_length=100,
        null=True,
        blank=False,
        editable=False,
    )
    owner_id = models.PositiveBigIntegerField(
        null=True,
        blank=False,
        editable=False,
    )
    verification_level = models.PositiveSmallIntegerField(
        null=True,
        blank=False,
        editable=False,
    )
    system_channel_id = models.PositiveBigIntegerField(
        null=True,
        blank=False,
        editable=False,
    )
    rules_channel_id = models.PositiveBigIntegerField(
        null=True,
        blank=False,
        editable=False,
    )
    large = models.BooleanField(
        null=True,
        blank=False,
        editable=False,
    )
    unavailable = models.BooleanField(
        null=True,
        blank=False,
        editable=False,
    )
    member_count = models.IntegerField(
        null=True,
        blank=False,
        editable=False,
    )

    def get_icon_url(self) -> Union[str, None]:
        ACCEPTED_FORMATS = ("png", "jpeg", "webp", "gif")
        guild_id: Snowflake = self.details.get("id")
        guild_icon: str = self.details.get("icon")
        if not guild_icon:
            return None

        animated: bool = True if guild_icon.startswith("a_") else False
        fmt: str = get_best_file_format(
            ACCEPTED_FORMATS,
            PREFERED_STILL_IMAGE_FORMATS if not animated else PREFERED_ANIMATED_IMAGE_FORMATS,
        )
        return f"{IMAGE_BASE_URL}icons/{guild_id}/{guild_icon}.{fmt}"

    def is_icon_url_live(self) -> bool:
        if self.get_icon_url():
            r: Response = requests.get(self.get_icon_url())
            return r.status_code == requests.codes.ok
        return False

    def get_splash_url(self) -> Union[str, None]:
        ACCEPTED_FORMATS = ("png", "jpeg", "webp", "gif")
        guild_id: Snowflake = self.details.get("id")
        guild_splash: str = self.details.get("splash")
        if not guild_splash:
            return None

        fmt: str = get_best_file_format(ACCEPTED_FORMATS, PREFERED_STILL_IMAGE_FORMATS)
        return f"{IMAGE_BASE_URL}splashes/{guild_id}/{guild_splash}.{fmt}"

    def is_splash_url_live(self) -> bool:
        if self.get_splash_url():
            r: Response = requests.get(self.get_splash_url())
            return r.status_code == requests.codes.ok
        return False

    def get_discovery_splash_url(self) -> Union[str, None]:
        ACCEPTED_FORMATS = ("png", "jpeg", "webp", "gif")
        guild_id: Snowflake = self.details.get("id")
        guild_discovery_splash: str = self.details.get("discovery_splash")
        if not guild_discovery_splash:
            return None

        fmt = get_best_file_format(ACCEPTED_FORMATS, PREFERED_STILL_IMAGE_FORMATS)
        return f"{IMAGE_BASE_URL}discovery-splashes/{guild_id}/{guild_discovery_splash}.{fmt}"

    def is_discovery_splash_url_live(self) -> bool:
        if self.get_discovery_splash_url():
            r: Response = requests.get(self.get_discovery_splash_url())
            return r.status_code == requests.codes.ok
        return False

    def get_guild_features(self) -> List[str]:
        return self.details.get("features", [])

    @property
    def is_partnered(self) -> bool:
        if "PARTNERED" in self.get_guild_features():
            return True
        return False

    @property
    def has_vanity_url(self) -> bool:
        if "VANITY_URL" in self.get_guild_features():
            return True
        return False

    @property
    def is_verified(self) -> bool:
        if "VERIFIED" in self.get_guild_features():
            return True
        return False

    @property
    def has_mfa(self) -> bool:
        return self.details.get("mfa_level", MFALevel.NONE) != MFALevel.NONE

    def get_owner(self) -> Optional[GuildMember]:
        owner_id: Snowflake = self.details.get("owner_id")
        members: List[GuildMember] = self.details.get("members")
        owner: Optional[GuildMember] = None
        if owner_id:
            for member in members:
                if member.get("user", {}).get("id") == owner_id:
                    owner = member
                    break
        return owner

    def get_system_channel(self) -> Optional[Channel]:
        system_channel_id: Snowflake = self.details.get("system_channel_id")
        channels: List[Channel] = self.details.get("channels")
        system_channel: Optional[Channel] = None
        if system_channel_id:
            for channel in channels:
                if channel.get("id") == system_channel_id:
                    system_channel = channel
                    break
        return system_channel

    def get_rules_channel(self) -> Optional[Channel]:
        rules_channel_id: Snowflake = self.details.get("rules_channel_id")
        channels: List[Channel] = self.details.get("channels")
        rules_channel: Optional[Channel] = None
        if rules_channel_id:
            for channel in channels:
                if channel.get("id") == rules_channel_id:
                    rules_channel = channel
                    break
        return rules_channel

    def get_members(self) -> List[GuildMember]:
        return self.details.get("members", [])

    def get_channels(self) -> List[Channel]:
        return self.details.get("channels", [])

    def get_vanity_url(self) -> Optional[str]:
        if self.has_vanity_url:
            return self.details.get("vanity_url")
        return None

    @property
    def description(self) -> Optional[str]:
        return self.details.get("description")

    def explode_details(self) -> None:
        # Explode the details field the relevant data into the relevant fields
        if Snowflake(self.details.get("id")) != Snowflake(self.id):
            raise ValueError("Guild ID does not match guild ID in details")

        self.preferred_locale = self.details.get("preferred_locale", "en-US")
        self.name = self.details.get("name")
        self.owner_id = self.details.get("owner_id")
        self.verification_level = self.details.get("verification_level")
        self.system_channel_id = self.details.get("system_channel_id")
        self.rules_channel_id = self.details.get("rules_channel_id")
        self.large = self.details.get("large")
        self.unavailable = self.details.get("unavailable")
        self.member_count = self.details.get("member_count")

    def get_details_from_api(self) -> bool:
        from community.discord.http import Client

        client: Client = Client().auth()
        r = client.get_guild(self.id)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            return False
        else:
            if r.status_code == requests.codes.ok:
                self.details = r.json()
                return True
        return False

    def save(self, *args, **kwargs) -> None:
        self.explode_details()
        return super().save(*args, **kwargs)

    @property
    def handle(self) -> str:
        return f"discord-{self.id}"
