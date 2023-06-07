from .HTTP import HTTPClient
from .typings import API_VERSION, SESSION
from typing import Union

from asyncio import AbstractEventLoop
from time import sleep


class Client(HTTPClient):

    def __init__(
            self,
            api_version: API_VERSION,
            session: SESSION = None,
            loop: AbstractEventLoop = None,
            logger: bool = True
    ):
        super().__init__(api_version, session, loop, logger)

    def login(self, token: Union[str, list[str]]):
        if self.logger._status:
            self.logger.info("Checking the provided tokens")
        self._tokens = token
        self._check_tokens()
        sleep(1)

    async def send_message(self, channel_id: int, message_content: str):
        for user in self.users:
            await user.send_message(channel_id, message_content)


