from __future__ import annotations

from typing import TYPE_CHECKING, Union, Optional

if TYPE_CHECKING:
    from .http import CustomSession

from .typings import AUTH_HEADER, RGB_COLOR
from .logger import Logger
from .enums import ChannelType
from .permissionbuilder import PermissionBuilder

from urllib.parse import quote
from asyncio import AbstractEventLoop
from aiohttp import ClientResponse
from logging import getLogger


class UserClient:
    """
    :class:`UserClient` Is the class responsible for the user account.

    :param data: Dict with account data - such as token, name, id.
    :param session: Session to send requests in methods
    """

    def __init__(self, data: dict, session: CustomSession):
        self._session: CustomSession = session
        self._logger: Logger = getLogger("Logger")  # pyright: ignore

        self.data: dict = data
        self._endpoint: str = self.data["endpoint"]
        self.token: str = self.data["token"]
        self.name: str = self.data["username"]
        self.discriminator: str = f"#{self.data['discriminator']}"
        self.id: int = self.data["id"]

        self._auth_header: AUTH_HEADER = AUTH_HEADER(
            authorization=self.token
        )

    def __repr__(self):
        return f"<UserClient(name={self.name}, discriminator={self.discriminator}, id={self.id})>"

    async def send_message(self, channel_id: int, message_content: str) -> ClientResponse:
        """
        The send_message function sends a message to the specified channel.

        :param channel_id: Specify the channel to send the message to
        :param message_content: content of the message
        """

        _url = self._endpoint + f"channels/{channel_id}/messages"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        payload: dict = {
            "content": message_content
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.warning(
                f"Request POST channels/{channel_id}/messages failed.\n -> {self} {await response.json()}")

        return response

    async def delete_channel(self, channel_id: int) -> ClientResponse:
        """
        The delete_channel function deletes a channel from the server.

        :param channel_id: Specify the channel that is to be deleted
        """

        _url = self._endpoint + f"channels/{channel_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE channels/{channel_id} failed.\n -> {self} {await response.json()}")

        return response

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType,
                             topic: Optional[str] = None, user_limit: Optional[int] = None,
                             position: Optional[int] = None, nsfw: Optional[bool] = False) -> ClientResponse:
        """
        The create_channel function creates a channel in the specified guild.

        :param guild_id: Specify the guild id of the server you want to create a channel in
        :param name: Specify the name of the channel
        :param channel_type: Specify what type of channel you want to create
        :param topic: Set the topic of the channel
        :param user_limit: Set the maximum number of users allowed in a voice channel
        :param position: Set the position of the channel in the list
        :param nsfw: Determine whether the channel is nsfw or not
        """

        _url = self._endpoint + f"guilds/{guild_id}/channels"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        payload: dict = {
            "name": name,
            "type": channel_type.value,
            "topic": topic,
            "user_limit": user_limit,
            "position": position,
            "nsfw": nsfw
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        if response.status not in (201, 429) and self._logger._status:
            self._logger.error(
                f"Request POST /guilds/{guild_id}/channels failed.\n -> {self} {await response.json()}")

        return response

    async def get_channels(self, guild_id: int) -> ClientResponse:
        """
        The get_channels function is a coroutine that takes in a guild_id and returns an ClientResponse object.
        The function can return the data of all channels on the server

        :param guild_id: Specify the guild id of the server you want to get channels from
        """

        _url = self._endpoint + f"guilds/{guild_id}/channels"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/channels failed.\n -> {self} {await response.json()}.")

        return response

    async def create_role(self,
                                guild_id: int,
                                name: str,
                                color: Optional[RGB_COLOR] = None,
                                hoist: Optional[bool] = False,
                                permissions: Union[PermissionBuilder, int, None] = None) -> ClientResponse:

        """
        The create_role function creates a role in the specified guild.

        :param guild_id: Specify the guild in which you want to create a role
        :param name: Set the name of the role
        :param color: Set the color of the role
        :param hoist: Determine whether the role should be displayed separately in the user list
        :param permissions: Set the permissions for the role
        """

        _url = self._endpoint + f"guilds/{guild_id}/roles"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        if color:
            r, g, b = color.values()
            _color = (r << 16) + (g << 8) + b  # pyright: ignore
        else:
            _color: int = 0  # pyright: ignore

        if not permissions:
            _permissions: int = 0
        else:
            _permissions: int = permissions.value  # pyright: ignore

        json: dict = {
            "name": name,
            "hoist": hoist,
            "color": _color,
            "permissions": _permissions
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=json)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request POST guilds/{guild_id}/roles failed.\n -> {self} {await response.json()}")

        return response

    async def get_roles(self, guild_id: int) -> ClientResponse:
        """
        get_roles returns a list of data with all the roles on the server

        :param guild_id: Specify the guild id of the server you want to get roles from
        """

        _url = self._endpoint + f"guilds/{guild_id}/roles"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/roles failed.\n -> {self} {await response.json()}")

        return response

    async def delete_role(self, guild_id: int, role_id: int) -> ClientResponse:
        """
        The delete_role function deletes a role from the guild.

        :param guild_id: Specify the guild that you want to delete a role from
        :param role_id: Specify the role_id to be deleted
        """

        _url = self._endpoint + f"guilds/{guild_id}/roles/{role_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/roles/{role_id} failed.\n -> {self} {await response.json()}")

        return response

    async def get_bans(self, guild_id: int) -> ClientResponse:
        """
        The get_bans function returns a list of banned users in the guild.

        :param guild_id: Specify the guild id of the server you want to get banned users from

        """
        _url = self._endpoint + f"guilds/{guild_id}/bans"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/bans failed.\n -> {self} {await response.json()}")

        return response

    async def unban_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The unban_member function unban a user from the guild.

        :param guild_id: Specify the guild that you want to unban a member from
        :param user_id: Specify the user id of the member to unban
        """

        _url = self._endpoint + f"guilds/{guild_id}/bans/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/bans/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def ban_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The ban_member function is used to ban a member from the guild.

        :param guild_id: Specify the guild that you want to ban a user from
        :param user_id: Specify the user that is to be banned
        """

        _url = self._endpoint + f"guilds/{guild_id}/bans/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: PUT -> {_url}")

        response: ClientResponse = await self._session.request(
            method="PUT", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request PUT guilds/{guild_id}/bans/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def kick_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The kick_member function kicks a member from the guild.

        :param guild_id: Specify the guild that you want to kick a user from
        :param user_id: Identify the user to be kicked
        """

        _url = self._endpoint + f"guilds/{guild_id}/members/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/members/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def get_member(self, guild_id: int, user_id: int) -> ClientResponse:
        """
        The get_member function is used to get a member from the guild.

        :param guild_id: Specify the guild that you want to get a member from
        :param user_id: Specify the user id of the member you want to get
        """

        _url = self._endpoint + f"guilds/{guild_id}/members/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/members/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def edit_member(self, guild_id: int, user_id: int,
                          nickname: Optional[str] = None,
                          add_roles: Optional[list[int]] = None,
                          remove_roles: Optional[list[int]] = None) -> ClientResponse:

        """
        The edit_member function allows you to edit a member of a guild.

        :param guild_id: Specify the guild that you want to edit a member in
        :param user_id: Specify the user that you want to edit
        :param nickname: Change the nickname of a user in a guild
        :param add_roles: Add roles to a user
        :param remove_roles: Remove roles from a user
        """

        json: dict = {}

        if add_roles or remove_roles:
            user_response: ClientResponse = await self.get_member(guild_id, user_id)
            user_data: dict = await user_response.json()

            roles: Union[None, list[str]] = user_data.get("roles")

            roles_list: list[str] = [] if not roles else roles

            if add_roles:
                for _role in add_roles:
                    roles_list.append(str(_role))

            if remove_roles:
                for _role in remove_roles:
                    try:
                        roles_list.remove(str(_role))
                    except ValueError:
                        pass
            json["roles"] = roles

        if nickname:
            json["nick"] = nickname

        _url = self._endpoint + f"guilds/{guild_id}/members/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: PATCH -> {_url}")

        response: ClientResponse = await self._session.request(
            method="PATCH", url=_url, headers=self._auth_header, json=json)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request PATCH guilds/{guild_id}/members/{user_id} failed.\n -> {self} {await response.json()}")

        return response

    async def add_reaction(self, channel_id: int, message_id: int, emoji: str) -> ClientResponse:
        """
        The add_reaction function adds a reaction to the message with the given ID in the channel with
        the given ID. The emoji parameter is a string that must be an emoticon. Example: \N{FIRE}

        :param channel_id: Specify which channel_id the message is in
        :param message_id: Message ID that you want to add a reaction to
        :param emoji: A reaction to add to the message
        """

        emoji = quote(emoji)

        _url = self._endpoint + f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me"

        if self._logger._status:
            self._logger.debug(f"Sending request: PUT -> {_url}")

        response: ClientResponse = await self._session.request(
            method="PUT", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request PUT channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me failed.\n -> {self} {await response.json()}")

        return response

    async def get_reactions(self, channel_id: int, message_id: int, emoji: str) -> ClientResponse:
        """
        The get_reactions function returns a ClientResponse with
        list of users that reacted with the specified emoji.

        :param channel_id: Identify the channel that contains the message
        :param message_id: Identify the message that is being reacted to
        :param emoji: Specify the emoji to get reactions for
        """

        emoji = quote(emoji)

        _url = self._endpoint + f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request GET channels/{channel_id}/messages/{message_id}/reactions/{emoji}/ failed.\n -> {self} {await response.json()}")

        return response

    async def delete_reaction(self, channel_id: int, message_id: int, user_id: int, emoji: str) -> ClientResponse:
        """
        The delete_reaction function is used to delete a reaction from a message.

        :param channel_id: Specify the channel where the message is located
        :param message_id: Identify the message that you want to delete a reaction from
        :param user_id: Specify the user whose reaction is to be deleted
        :param emoji: Specify the emoji to be deleted
        """

        emoji = quote(emoji)

        _url = self._endpoint + f"channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status not in (204, 429) and self._logger._status:
            self._logger.error(
                f"Request DELETE channels/{channel_id}/messages/{message_id}/reactions/{emoji}/{user_id} failed.\n -> {self} {await response.json()}")

        return response


