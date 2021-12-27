import enum


class UserFlags(enum.IntFlag):
    STAFF = 0
    PARTNER = 1
    HYPESQUAD = 2
    BUG_HUNTER_LEVEL_1 = 3
    HYPESQUAD_ONLINE_HOUSE_1 = 6
    HYPESQUAD_ONLINE_HOUSE_2 = 7
    HYPESQUAD_ONLINE_HOUSE_3 = 8
    PREMIUM_EARLY_SUPPORTER = 9
    TEAM_PSEUDO_USER = (
        10  # This is a user that is not a real user, but is used for team-based permissions
    )
    BUG_HUNTER_LEVEL_2 = 14
    VERIFIED_BOT = 16
    VERIFIED_DEVELOPER = 17
    CERTIFIED_MODERATOR = 18
    BOT_HTTP_INTERACTIONS = 19


class PremiumTypes(enum.Int):
    NONE = 0
    NITRO_CLASSIC = 1
    NITRO = 2


class VerificationLevel(enum.Int):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    VERY_HIGH = 4


class DefaultMessageNotifications(enum.Int):
    ALL_MESSAGES = 0
    ONLY_MENTIONS = 1


class ExplicitContentFilterLevel(enum.Int):
    DISABLED = 0
    MEMBERS_WITHOUT_ROLES = 1
    ALL_MEMBERS = 2


class MFALevel(enum.Int):
    NONE = 0
    ELEVATED = 1


class SystemChannelFlags(enum.IntFlag):
    SUPPRESS_JOIN_NOTIFICATIONS = 0
    SUPPRESS_PREMIUM_SUBSCRIPTIONS = 1
    SUPPRESS_GUILD_REMINDER_NOTIFICATIONS = 2
    SUPPRESS_JOIN_NOTIFICATION_REPLIES = 3


class ChannelTypes(enum.Int):
    GUILD_TEXT = 0
    DM = 1
    GUILD_VOICE = 2
    GROUP_DM = 3
    GUILD_CATEGORY = 4
    GUILD_NEWS = 5
    GUILD_STORE = 6
    GUILD_NEWS_THREAD = 10
    GUILD_PUBLIC_THREAD = 11
    GUILD_PRIVATE_THREAD = 12
    GUILD_STAGE_VOICE = 13


class OverwriteType(enum.Int):
    ROLE = 0
    USER = 1


class Permissions(enum.IntFlag):
    CREATE_INSTANT_INVITE = 0
    KICK_MEMBERS = 1
    BAN_MEMBERS = 2
    ADMINISTRATOR = 3
    MANAGE_CHANNELS = 4
    MANAGE_GUILD = 5
    ADD_REACTIONS = 6
    VIEW_AUDIT_LOG = 7
    PRIORITY_SPEAKER = 8
    STREAM = 9
    VIEW_CHANNEL = 10
    SEND_MESSAGES = 11
    SEND_TTS_MESSAGES = 12
    MANAGE_MESSAGES = 13
    EMBED_LINKS = 14
    ATTACH_FILES = 15
    READ_MESSAGE_HISTORY = 16
    MENTION_EVERYONE = 17
    USE_EXTERNAL_EMOJIS = 18
    VIEW_GUILD_INSIGHTS = 19
    CONNECT = 20
    SPEAK = 21
    MUTE_MEMBERS = 22
    DEAFEN_MEMBERS = 23
    MOVE_MEMBERS = 24
    USE_VAD = 25
    CHANGE_NICKNAME = 26
    MANAGE_NICKNAMES = 27
    MANAGE_ROLES = 28
    MANAGE_WEBHOOKS = 29
    MANAGE_EMOJIS_AND_STICKERS = 30
    USE_APPLICATION_COMMANDS = 31
    REQUEST_TO_SPEAK = 32
    MANAGE_EVENTS = 33
    MANAGE_THREADS = 34
    CREATE_PUBLIC_THREADS = 35
    CREATE_PRIVATE_THREADS = 36
    USE_EXTERNAL_STICKERS = 37
    SEND_MESSAGES_IN_THREADS = 38
    START_EMBEDDED_ACTIVITIES = 39
    MODERATE_MEMBERS = 40


class VideoQualityModes(enum.Int):
    AUTO = 1
    FULL = 2


class ActivityTypes(enum.Int):
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    CUSTOM = 4
    COMPETING = 5


class ActivityFlags(enum.IntFlag):
    """activity flags ORd together, describes what the payload includes"""

    INSTANCE = 0
    JOIN = 1
    SPECTATE = 2
    JOIN_REQUEST = 3
    SYNC = 4
    PLAY = 5
    PARTY_PRIVACY_FRIENDS = 6
    PARTY_PRIVACY_VOICE_CHANNEL = 7
    EMBEDDED = 8


class PresenceStatus(enum.Enum):
    IDLE = "idle"
    DND = "dnd"
    ONLINE = "online"
    OFFLINE = "offline"


class PremiumTier(enum.Int):
    NONE = 0
    TIER_1 = 1
    TIER_2 = 2
    TIER_3 = 3


class GuildNSFWLevel(enum.Int):
    DEFAULT = 0
    EXPLICIT = 1
    SAFE = 2
    AGE_RESTRICTED = 3


class StagePrivacyLevel(enum.Int):
    PUBLIC = 1
    GUILD_ONLY = 2


class StickerType(enum.Int):
    STANDARD = 1
    GUILD = 2


class StickerFormat(enum.Int):
    PNG = 1
    APNG = 2
    LOTTIE = 3


class ScheduledEventPrivacyLevel(enum.Int):
    GUILD_ONLY = 2


class ScheduledEventStatus(enum.Int):
    SCHEDULED = 1
    ACTIVE = 2
    COMPLETED = 3
    CANCELED = 4


class ScheduledEventEntityType(enum.Int):
    STAGE_INSTANCE = 1
    VOICE = 2
    EXTERNAL = 3
