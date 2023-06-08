from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .HTTP import CustomSession

from .typings import AUTH_HEADER, RGB_COLOR
from .Logger import Logger
from .enums import ChannelType
from .PermissionBuilder import PermissionBuilder

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

    async def send_message(self, channel_id: int, message_content: str):
        _url = self._endpoint + f"channels/{channel_id}/messages"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        payload: dict = {
            "content": message_content
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        if response.status == 403 and self._logger._status:
            self._logger.warning(
                f"Request POST channels/{channel_id}/messages failed.\n -> {self} user does not have permissions to write on this channel")

        elif response.status == 400 and self._logger._status:
            self._logger.error(
                f"Request POST channels/{channel_id}/messages failed.\n -> Probably {self} does not have access to this server")

        return response

    async def delete_channel(self, channel_id: int):
        _url = self._endpoint + f"channels/{channel_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request DELETE channels/{channel_id} failed.\n -> {self} user does not have Manage_guild or Manage_thread permissions")

        elif response.status == 400 and self._logger._status:
            self._logger.error(
                f"Request DELETE channels/{channel_id} failed.\n -> Probably {self} does not have access to this server")

        return response

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType,
                             topic: str = None, user_limit: int = None, position: int = None, nsfw: bool = False):
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

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request POST /guilds/{guild_id}/channels failed.\n -> {self} user does not have Manage_channels or Manage_roles permissions")

        elif response.status == 400 and self._logger._status:
            self._logger.error(
                f"Request POST guilds/{guild_id}/channels failed.\n -> Probably {self} does not have access to this server")

        return response

    async def get_channels(self, guild_id: int):
        _url = self._endpoint + f"guilds/{guild_id}/channels"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/channels failed.\n -> {self} user does not have Manage_channels permission.")

        elif response.status == 400 and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/channels failed.\n -> Probably {self} does not have access to this server")

        return response

    async def create_role(self,
                                guild_id: int,
                                name: str,
                                color: RGB_COLOR = None,
                                hoist: bool = False,
                                permissions: PermissionBuilder = None):

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

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request POST guilds/{guild_id}/roles failed.\n -> {self} user does not have Manage_roles permission.")

        elif response.status == 400 and self._logger._status:
            self._logger.error(
                f"Request POST guilds/{guild_id}/roles failed.\n -> Probably {self} does not have access to this server")

        return response

    async def get_roles(self, guild_id: int):
        _url = self._endpoint + f"guilds/{guild_id}/roles"

        if self._logger._status:
            self._logger.debug(f"Sending request: GET -> {_url}")

        response: ClientResponse = await self._session.request(
            method="GET", url=_url, headers=self._auth_header)

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/roles failed.\n -> {self} user does not have Manage_roles permission.")
        elif response.status == 400 and self._logger._status:
            self._logger.error(
                f"Request GET guilds/{guild_id}/roles failed.\n -> Probably {self} does not have access to this server")

        return response

    async def delete_role(self, guild_id: int, role_id: int):
        _url = self._endpoint + f"guilds/{guild_id}/roles/{role_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/roles/{role_id} failed.\n -> {self} user does not have Manage_roles permission.")

        return response

    async def ban_member(self, guild_id: int, user_id: int):
        _url = self._endpoint + f"guilds/{guild_id}/bans/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: PUT -> {_url}")

        response: ClientResponse = await self._session.request(
            method="PUT", url=_url, headers=self._auth_header)

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request PUT guilds/{guild_id}/bans/{user_id} failed.\n -> {self} user does not have Ban_Members permission. Or the selected person is higher in the hierarchy")

        return response

    async def kick_member(self, guild_id: int, user_id: int):
        _url = self._endpoint + f"guilds/{guild_id}/members/{user_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        if response.status == 403 and self._logger._status:
            self._logger.error(
                f"Request DELETE guilds/{guild_id}/members/{user_id} failed.\n -> {self} user does not have Kick_Members permission. Or the selected person is higher in the hierarchy")

        return response