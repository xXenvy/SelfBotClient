from .typings import SESSION, AUTH_HEADER
from .Logger import Logger
from .enums import ChannelType

from asyncio import AbstractEventLoop
from aiohttp import ClientResponse
from logging import getLogger


class UserClient:

    def __init__(self, data: dict, session: SESSION, loop: AbstractEventLoop):
        self._session: SESSION = session
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
        method="POST", url=_url, headers=self._auth_header, data=payload)

        response.raise_for_status()

        return response

    async def delete_channel(self, channel_id: int):
        _url = self._endpoint + f"channels/{channel_id}"

        if self._logger._status:
            self._logger.debug(f"Sending request: DELETE -> {_url}")

        response: ClientResponse = await self._session.request(
            method="DELETE", url=_url, headers=self._auth_header)

        response.raise_for_status()

        return response

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType):
        _url = self._endpoint + f"guilds/{guild_id}/channels"

        if self._logger._status:
            self._logger.debug(f"Sending request: POST -> {_url}")

        payload: dict = {
            "name": name,
            "type": channel_type.value
        }

        response: ClientResponse = await self._session.request(
            method="POST", url=_url, headers=self._auth_header, json=payload)

        response.raise_for_status()

        return response
