from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .http import CustomSession

from .typings import AUTH_HEADER, RGB_COLOR
from .logger import Logger
from .enums import ChannelType
from .permissionbuilder import PermissionBuilder

from asyncio import AbstractEventLoop
from aiohttp import ClientResponse
from logging import getLogger


class UserClient:

    def __init__(self, data: dict, session: CustomSession, loop: AbstractEventLoop):
        """
        The __init__ function is called when the class is instantiated.
        It sets up all of the variables that are needed for other functions to work properly.


        :param self: Represent the instance of the class
        :param data: dict: Store the data that is passed into the class
        :param session: CustomSession: Pass the session to the class
        :param loop: AbstractEventLoop: Create a new event loop
        :return: None
        """

        self._session: CustomSession = session
        self._loop: AbstractEventLoop = loop
        self._logger: Logger = getLogger("Logger")

        self.data: dict = data
        self._endpoint: str = self.data.get("endpoint")
        self.token: str = self.data.get("token")
        self.name: str = self.data.get("username")
        self.discriminator: str = f"#{self.data.get('discriminator')}"
        self.id: int = self.data.get("id")

        self._auth_header: AUTH_HEADER = AUTH_HEADER(
            authorization=self.token
        )

    def __repr__(self):
        return f"<UserClient(name={self.name}, discriminator={self.discriminator}, id={self.id})>"

    async def send_message(self, channel_id: int, message_content: str) -> ClientResponse:
        """
        The send_message function sends a message to the specified channel.

        :param self: Represent the instance of the class
        :param channel_id: int: Specify the channel that you want to send a message to
        :param message_content: str: Send a message to the channel
        :return: A clientresponse object
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
        The delete_channel function deletes a channel.
            Parameters:
                channel_id (int): The ID of the channel to delete.

        :param self: Access the class attributes and methods
        :param channel_id: int: Specify which channel to delete
        :return: A clientresponse object
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
                             topic: str = None, user_limit: int = None, position: int = None, nsfw: bool = False) -> ClientResponse:
        """
        The create_channel function creates a new channel in the specified guild.

        :param self: Refer to the current instance of a class
        :param guild_id: int: Specify the server that you want to create a channel in
        :param name: str: Set the name of the channel
        :param channel_type: ChannelType: Specify the type of channel that is being created
        :param topic: str: Set the topic of the channel
        :param user_limit: int: Set the maximum number of users that can be in a voice channel
        :param position: int: Set the position of the channel in the server
        :param nsfw: bool: Determine if the channel is nsfw or not
        :return: A clientresponse object
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
        The get_channels function returns a list of channel objects for the guild.
            Args:
                guild_id (int): The id of the server to get channels from.

        :param self: Represent the instance of the class
        :param guild_id: int: Get the channels of a specific guild
        :return: A clientresponse object
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
                                color: RGB_COLOR = None,
                                hoist: bool = False,
                                permissions: PermissionBuilder = None) -> ClientResponse:

        """
        The create_role function creates a new role in the specified guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the server you want to create a role in
        :param name: str: Set the name of the role
        :param color: RGB_COLOR: Set the color of the role
        :param hoist: bool: Determine if the role should be displayed separately in the user list
        :param permissions: PermissionBuilder: Set the permissions of the role
        :return: A clientresponse object
        """

        _url = self._endpoint + f"guilds/{guild_id}/roles"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        if color:
            r, g, b = color.values()
            color = (r << 16) + (g << 8) + b
        else:
            color = 0

        if not permissions:
            permissions = 0
        else:
            permissions = permissions.value

        json: dict = {
            "name": name,
            "hoist": hoist,
            "color": color,
            "permissions": permissions
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=json)

        if response.status not in (200, 429) and self._logger._status:
            self._logger.error(
                f"Request POST guilds/{guild_id}/roles failed.\n -> {self} {await response.json()}")

        return response

    async def get_roles(self, guild_id: int) -> ClientResponse:
        """
        The get_roles function returns a list of roles for the specified guild.
            Parameters:
                guild_id (int): The ID of the guild to get roles from.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify which guild you want to get the roles from
        :return: A clientresponse object
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

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild id of the role you want to delete
        :param role_id: int: Specify which role to delete
        :return: A clientresponse object
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
        The unban_member function is used to unban a member from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that you want to unban a member from
        :param user_id: int: Specify the user id of the member that you want to unban
        :return: A clientresponse object
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

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild id of the server you want to ban a member from
        :param user_id: int: Specify the user id of the person you want to ban
        :return: A clientresponse object
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
        The kick_member function is used to kick a member from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: The ID of the guild you want to kick a member from.
        :param user_id: int: The ID of the user you want to kick.
        :return: A clientresponse object
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
        The get_member function is used to get a member of the guild.

        :param self: Access the class attributes and methods
        :param guild_id: int: Specify the guild id of the server you want to get a member from
        :param user_id: int: Get the user's id
        :return: A clientresponse object
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
                          nickname: str = None,
                          add_roles: list[int] = None,
                          remove_roles: list[int] = None) -> ClientResponse:

        """
        The edit_member function allows you to edit a member of the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild id of the server you want to edit
        :param user_id: int: Specify the user to edit
        :param nickname: str: Set the nickname of a member
        :param add_roles: list[int]: Add roles to a user
        :param remove_roles: list[int]: Remove roles from a user
        :return: A clientresponse object or None
        """

        json: dict = {}

        if add_roles or remove_roles:
            user_response: ClientResponse = await self.get_member(guild_id, user_id)
            user_data: dict = await user_response.json()

            roles: list[str] = user_data.get("roles")
            if not roles:
                roles: list[str] = []

            if add_roles:
                for _role in add_roles:
                    roles.append(str(_role))
            if remove_roles:
                for _role in remove_roles:
                    try:
                        roles.remove(str(_role))
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

