from enum import Enum


__all__: tuple[str, ...] = ("ChannelType", "Permissions", "Discord",
                            "ActivityPlatform", "ActivityStatus", "ActivityType")


class Discord(Enum):
    ENDPOINT = "https://discord.com/api/v{}/"
    ENDPONT_GATEWAY = "wss://gateway.discord.gg/?v={}&encoding=json"


class Components(Enum):
    BUTTON = 2
    DROPDOWN = 3


class ActivityStatus(Enum):
    ONLINE = "online"
    DND = "dnd"
    IDLE = "idle"
    OFFLINE = "offline"


class ActivityPlatform(Enum):
    DESKTOP = "Windows"
    MOBILE = "Android"


class ActivityType(Enum):
    GAME = 0
    STREAMING = 1
    LISTENING = 2
    WATCHING = 3
    COMPETING = 5


class ChannelType(Enum):

    TEXT_CHANNEL = 0
    VOICE_CHANNEL = 2
    CATEGORY_CHANNEL = 4


class Permissions(Enum):
    CREATE_INSTANT_INVITE = 1 << 0
    KICK_MEMBERS = 1 << 1
    BAN_MEMBERS = 1 << 2
    ADMINISTRATOR = 1 << 3
    MANAGE_CHANNELS = 1 << 4
    MANAGE_GUILD = 1 << 5
    ADD_REACTIONS = 1 << 6
    VIEW_AUDIT_LOG = 1 << 7
    PRIORITY_SPEAKER = 1 << 8
    STREAM = 1 << 9
    VIEW_CHANNEL = 1 << 10
    SEND_MESSAGES = 1 << 11
    SEND_TTS_MESSAGES = 1 << 12
    MANAGE_MESSAGES = 1 << 13
    EMBED_LINKS = 1 << 14
    ATTACH_FILES = 1 << 15
    READ_MESSAGE_HISTORY = 1 << 16
    MENTION_EVERYONE = 1 << 17
    USE_EXTERNAL_EMOJIS = 1 << 18
    VIEW_GUILD_INSIGHTS = 1 << 19
    CONNECT = 1 << 20
    SPEAK = 1 << 21
    MUTE_MEMBERS = 1 << 22
    DEAFEN_MEMBERS = 1 << 23
    MOVE_MEMBERS = 1 << 24
    CHANGE_NICKNAME = 1 << 26
    MANAGE_NICKNAMES = 1 << 27
    MANAGE_ROLES = 1 << 28
    MANAGE_WEBHOOKS = 1 << 29
    MANAGE_THREADS = 1 << 34
    CREATE_PUBLIC_THREADS = 1 << 35
    CREATE_PRIVATE_THREADS = 1 << 36
    MODERATE_MEMBERS = 1 << 40
