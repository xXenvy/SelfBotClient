from .typings import API_VERSION, SESSION, AUTH_HEADER, METHOD
from .errors import UnSupportedApiVersion, UnSupportedTokenType
from .enums import Discord
from .Logger import Logger
from .User import UserClient

from typing import Union
from aiohttp import ClientSession, ClientResponse
from asyncio import AbstractEventLoop, get_event_loop


class HTTPClient:

    def __init__(
            self,
            api_version: API_VERSION,
            session: SESSION = None,
            loop: AbstractEventLoop = None,
    ):
        if api_version not in (9, 10):
            raise UnSupportedApiVersion

        self.api_version: int = api_version
        self.endpoint: str = Discord.ENDPOINT.value.format(self.api_version)
        self.loop: AbstractEventLoop = loop if loop else get_event_loop()

        self._tokens: Union[str, list, None] = None
        self.logger: Logger = Logger().logger
        self.session: Union[SESSION, None] = None

        self.connected: bool = False
        self.users: list[UserClient] = []
        self.loop.run_until_complete(self.create_session(session))

    async def create_session(self, session: Union[ClientSession, None]):
        self.session: SESSION = session if session else ClientSession()

    def _check_tokens(self):

        async def _check(_type: Union[type[list], type[str]]):
            _url: str = self.endpoint + "users/@me"
            if _type == str:
                header: AUTH_HEADER = AUTH_HEADER(authorization=self._tokens)
                response: ClientResponse = await self.session.get(_url, headers=header)
                if response.status != 200:
                    self.logger.warning(
                        f"An invalid token has been provided: {self._tokens} | The token will be automatically deleted")
                    self._tokens = []
                else:
                    data = await response.json()
                    data["token"] = self._tokens
                    self.users.append(UserClient(data, self.session))

                    self._tokens = [self._tokens]

            elif _type == list:
                for token in self._tokens:

                    header: AUTH_HEADER = AUTH_HEADER(authorization=token)
                    response: ClientResponse = await self.session.get(_url, headers=header)
                    if response.status != 200:
                        self.logger.warning(
                            f"An invalid token has been provided: {token} | The token will be automatically deleted")

                        self._tokens.remove(token)
                    else:
                        data = await response.json()
                        data["token"] = token

                        self.users.append(UserClient(data, self.session))

            self.logger.info(f"Checking of tokens successfully completed | Loaded ({len(self.users)}) tokens)")

        if not isinstance(self._tokens, list) and not isinstance(self._tokens, str):
            raise UnSupportedTokenType

        self.loop.run_until_complete(_check(type(self._tokens)))
        self.connected: bool = True

    def __del__(self):
        self.loop.run_until_complete(self.session.close())

    async def request(self, url: str, method: METHOD, headers: dict = None, data: dict = None) -> ClientResponse:
        url: str = self.endpoint + url
        self.logger.debug(f"Sending request: {method} -> {url}")

        response: ClientResponse = await self.session.request(method=method, url=url, headers=headers, data=data)
        response.raise_for_status()

        return response