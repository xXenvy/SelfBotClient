from enum import Enum


class Events(Enum):
    READY = "on_ready"

    MESSAGE_CREATE = "on_message_create"
    MESSAGE_DELETE = "on_message_delete"
    MESSAGE_UPDATE = "on_message_edit"

    MESSAGE_REACTION_REMOVE = "on_message_reaction_remove"
    MESSAGE_REACTION_ADD = "on_message_reaction_add"

    CHANNEL_DELETE = "on_channel_delete"
    CHANNEL_CREATE = "on_channel_create"
    CHANNEL_UPDATE = "on_channel_edit"

    GUILD_UPDATE = "on_guild_update"
    GUILD_ROLE_CREATE = "on_guild_role_create"
    GUILD_ROLE_DELETE = "on_guild_role_delete"
    GUILD_BAN_ADD = "on_guild_ban_add"
    GUILD_BAN_REMOVE = "on_guild_ban_remove"