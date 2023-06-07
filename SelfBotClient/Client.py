from .HTTP import HTTPClient
from .typings import API_VERSION, ClientResponse
from .enums import ChannelType

from typing import Union

from asyncio import AbstractEventLoop
from time import sleep


class Client(HTTPClient):

    def __init__(
            self,
            api_version: API_VERSION,
            loop: AbstractEventLoop = None,
            logger: bool = True
    ):
        super().__init__(api_version, loop, logger)

    def login(self, token: Union[str, list[str]]) -> None:
        if self.logger._status:
            self.logger.info("Checking the provided tokens")

        self._tokens: Union[str, list[str]] = token
        self._check_tokens()
        sleep(1)

    async def send_message(self, channel_id: int, message_content: str) -> Union[None, ClientResponse]:
        data = None

        for user in self.users:
            data = await user.send_message(channel_id, message_content)
        return data

    async def delete_channel(self, channel_id: int) -> Union[None, ClientResponse]:
        data = None

        for user in self.users:
            data = await user.delete_channel(channel_id)

        return data

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType,
                             topic: str = None, user_limit: int = None, position: int = None, nsfw: bool = False) -> Union[None, ClientResponse]:
        data = None

        for user in self.users:
            data = await user.create_channel(guild_id, name, channel_type, topic, user_limit, position, nsfw)
        return data

