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
    ):
        super().__init__(api_version, session, loop)

    def login(self, token: Union[str, list[str]]):
        self.logger.info("Checking the provided tokens")
        self._tokens = token
        self._check_tokens()
        sleep(1)


