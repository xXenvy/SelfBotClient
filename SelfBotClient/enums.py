from enum import Enum


class Discord(Enum):
    ENDPOINT: str = "https://discord.com/api/v{}/"


class ChannelType(Enum):

    TEXT_CHANNEL: int = 0
    VOICE_CHANNEL: int = 2
    CATEGORY_CHANNEL: int = 4