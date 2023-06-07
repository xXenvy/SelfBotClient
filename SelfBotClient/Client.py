from .HTTP import HTTPClient
from .typings import API_VERSION, ClientResponse
from .enums import ChannelType
from collections.abc import AsyncIterable

from typing import Union, Iterable

from asyncio import AbstractEventLoop
from time import sleep


class Client(HTTPClient):

    def __init__(
            self,
            api_version: API_VERSION,
            loop: AbstractEventLoop = None,
            logger: bool = True,
            request_latency: float = 0.1,
            ratelimit_additional_cooldown: float = 10
    ):

        super().__init__(api_version, loop, logger, request_latency, ratelimit_additional_cooldown)

    def login(self, token: Union[str, list[str]]) -> None:
        if self.logger._status:
            self.logger.info("Checking the provided tokens")

        self._tokens: Union[str, list[str]] = token
        self._check_tokens()
        sleep(1)

    async def send_message(self, channel_id: int, message_content: str) -> Union[None, AsyncIterable[ClientResponse]]:

        for user in self.users:
            response = await user.send_message(channel_id, message_content)
            yield response

    async def delete_channel(self, channel_id: int) -> Union[None, AsyncIterable[ClientResponse]]:

        for user in self.users:
            response = await user.delete_channel(channel_id)
            yield response

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType,
                             topic: str = None, user_limit: int = None, position: int = None, nsfw: bool = False) -> Union[None, AsyncIterable[ClientResponse]]:

        for user in self.users:
            response = await user.create_channel(guild_id, name, channel_type, topic, user_limit, position, nsfw)
            yield response


