from enum import Enum


class Discord(Enum):
    ENDPOINT: str = "https://discord.com/api/v{}/"


class ChannelType(Enum):

    TEXT_CHANNEL: int = 0
    VOICE_CHANNEL: int = 2
    CATEGORY_CHANNEL: int = 4


class Permissions(Enum):
    CREATE_INSTANT_INVITE: int = 1 << 0
    KICK_MEMBERS: int = 1 << 1
    BAN_MEMBERS: int = 1 << 2
    ADMINISTRATOR: int = 1 << 3
    MANAGE_CHANNELS: int = 1 << 4
    MANAGE_GUILD: int = 1 << 5
    ADD_REACTIONS: int = 1 << 6
    VIEW_AUDIT_LOG: int = 1 << 7
    PRIORITY_SPEAKER: int = 1 << 8
    STREAM: int = 1 << 9
    VIEW_CHANNEL: int = 1 << 10
    SEND_MESSAGES: int = 1 << 11
    SEND_TTS_MESSAGES: int = 1 << 12
    MANAGE_MESSAGES: int = 1 << 13
    EMBED_LINKS: int = 1 << 14
    ATTACH_FILES: int = 1 << 15
    READ_MESSAGE_HISTORY: int = 1 << 16
    MENTION_EVERYONE: int = 1 << 17
    USE_EXTERNAL_EMOJIS: int = 1 << 18
    VIEW_GUILD_INSIGHTS: int = 1 << 19
    CONNECT: int = 1 << 20
    SPEAK: int = 1 << 21
    MUTE_MEMBERS: int = 1 << 22
    DEAFEN_MEMBERS: int = 1 << 23
    MOVE_MEMBERS: int = 1 << 24
    CHANGE_NICKNAME: int = 1 << 26
    MANAGE_NICKNAMES: int = 1 << 27
    MANAGE_ROLES: int = 1 << 28
    MANAGE_WEBHOOKS: int = 1 << 29
    MANAGE_THREADS: int = 1 << 34
    CREATE_PUBLIC_THREADS: int = 1 << 35
    CREATE_PRIVATE_THREADS: int = 1 << 36
    MODERATE_MEMBERSL: int = 1 << 40