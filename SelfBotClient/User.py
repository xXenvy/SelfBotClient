from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .HTTP import CustomSession

from .typings import AUTH_HEADER
from .Logger import Logger
from .enums import ChannelType

from asyncio import AbstractEventLoop
from aiohttp import ClientResponse, client_exceptions
from logging import getLogger


class UserClient:

    def __init__(self, data: dict, session: CustomSession, loop: AbstractEventLoop):
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

        return response

    async def delete_channel(self, channel_id: int):
        _url = self._endpoint + f"channels/{channel_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        response.raise_for_status()

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

        try:
            response.raise_for_status()
        except client_exceptions.ClientResponseError as exception:
            if exception.status == 403 and self._logger._status:
                self._logger.error(
                f"Request POST {self} | /guilds/{guild_id}/channels failed. Missing permissions: manage_guild or manage_roles")

        return response
