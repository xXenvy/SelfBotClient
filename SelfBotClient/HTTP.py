from .typings import API_VERSION, AUTH_HEADER, METHOD
from .errors import UnSupportedApiVersion, UnSupportedTokenType, InvalidMethodType
from .enums import Discord
from .Logger import Logger
from .User import UserClient

from typing import Union, Awaitable, Any
from aiohttp import ClientSession, ClientResponse
from asyncio import AbstractEventLoop, get_event_loop, sleep


class CustomSession(ClientSession):

    def __init__(self, logger: Logger, *args: Any, **kwargs: Any):
        self.logger: Logger = logger
        self.logger_status = logger._status

        self.request_latency: float = kwargs.get("latency")
        self.ratelimit_additional_cooldown: float = kwargs.get("additional_cooldown")
        del kwargs["latency"]
        del kwargs["additional_cooldown"]

        super().__init__(*args, **kwargs)

    async def request(self, method: str, url: str, **kwargs: Any) -> ClientResponse:
        response = await super().request(method=method, url=url, **kwargs)

        if response.headers.get("Retry-After"):

            seconds = int(response.headers.get("Retry-After")) + self.ratelimit_additional_cooldown
            if self.logger_status:
                self.logger.warning(f"Ratelimit has been reached. Awaiting {seconds} seconds before next request.")

            await sleep(seconds)
        else:
            await sleep(self.request_latency)

        return response

    async def get(self, url: str, *, allow_redirects: bool = True, **kwargs: Any) -> ClientResponse:
        await sleep(1)
        response = await super().get(url=url, allow_redirects=allow_redirects, **kwargs)
        return response


class HTTPClient:

    def __init__(
            self,
            api_version: API_VERSION,
            loop: AbstractEventLoop = None,
            logger: bool = True,
            request_latency: float = 0.1,
            ratelimit_additional_cooldown: float = 10

    ):
        if api_version not in (9, 10):
            raise UnSupportedApiVersion

        self.request_latency: float = request_latency
        self.ratelimit_additional_cooldown: float = 10

        self.api_version: int = api_version
        self.endpoint: str = Discord.ENDPOINT.value.format(self.api_version)
        self.loop: AbstractEventLoop = loop if loop else get_event_loop()

        self._tokens: Union[str, list, None] = None
        self._logger_status: bool = logger

        self.logger: Logger = Logger().logger
        self.logger._status = self._logger_status
        self.session: Union[CustomSession, None] = None

        self.users: list[UserClient] = []
        self.loop.run_until_complete(self.create_session())

    async def create_session(self):
        self.session: CustomSession = CustomSession(self.logger, latency=self.request_latency, additional_cooldown=self.ratelimit_additional_cooldown)

    def _check_tokens(self):

        async def _check(_type: Union[type[list], type[str]]):
            _url: str = self.endpoint + "users/@me"
            if _type == str:
                header: AUTH_HEADER = AUTH_HEADER(authorization=self._tokens)
                response: ClientResponse = await self.session.get(_url, headers=header)
                if response.status != 200:
                    if self._logger_status:
                        self.logger.warning(
                            f"An invalid token has been provided: {self._tokens} | The token will be automatically deleted")
                else:
                    data = await response.json()
                    data["token"] = self._tokens
                    data["endpoint"] = self.endpoint
                    self.users.append(UserClient(data, self.session, self.loop))

                    self._tokens = [self._tokens]

            elif _type == list:
                for token in self._tokens:

                    header: AUTH_HEADER = AUTH_HEADER(authorization=token)
                    response: ClientResponse = await self.session.get(_url, headers=header)
                    if response.status != 200:
                        if self._logger_status:
                            self.logger.warning(
                                f"An invalid token has been provided: {token} | The token will be automatically deleted")

                    else:
                        data = await response.json()
                        data["token"] = token
                        data["endpoint"] = self.endpoint

                        self.users.append(UserClient(data, self.session, self.loop))

            if self._logger_status:
                self.logger.info(f"Checking of tokens successfully completed | Loaded ({len(self.users)}) tokens")

        if not isinstance(self._tokens, list) and not isinstance(self._tokens, str):
            raise UnSupportedTokenType

        self.loop.run_until_complete(_check(type(self._tokens)))

    def __del__(self):
        self.loop.run_until_complete(self.session.close())

    def run_async(self, function: Awaitable) -> None:
        self.loop.run_until_complete(function)

    async def request(self, url: str, method: METHOD, headers: dict = None, data: dict = None) -> ClientResponse:
        if method not in ("POST", "GET", "DELETE", "PATCH"):
            raise InvalidMethodType(method)

        url: str = self.endpoint + url

        if self._logger_status:
            self.logger.debug(f"Sending request: {method} -> {url}")

        response: ClientResponse = await self.session.request(method=method, url=url, headers=headers, json=data)
        response.raise_for_status()

        return response
