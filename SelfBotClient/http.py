from __future__ import annotations

from .typings import API_VERSION, AUTH_HEADER, METHOD
from .errors import UnSupportedApiVersion, UnSupportedTokenType, InvalidMethodType
from .enums import Discord
from .presence import ActivityBuilder
from .logger import Logger
from .user import UserClient
from .gateway.gateway import Gateway

from typing import Union, Awaitable, Any, Optional, TYPE_CHECKING
from aiohttp import ClientSession, ClientResponse, client_exceptions
from asyncio import AbstractEventLoop, sleep, get_event_loop

if TYPE_CHECKING:
    from .client import Client

__all__: tuple[str, ...] = ("HTTPClient", "ClientResponse", "CustomSession")


class CustomSession(ClientSession):

    def __init__(self, logger: Logger, *args: Any, **kwargs: Any):
        """
        The __init__ function sets up all of the variables that are needed for other functions to work properly.
        The super() function calls __init__ from the parent class, which in this case is ClientSession.

        :param logger: Pass the logger object to the class
        :param *args: Pass any additional arguments to the superclass
        :param **kwargs: Pass in additional parameters that are not explicitly defined
        """

        self.logger: Logger = logger
        self.logger_status = logger._status

        self.request_latency: float = kwargs["latency"]
        self.ratelimit_additional_cooldown: float = kwargs["additional_cooldown"]
        self.users: Optional[list[UserClient]] = kwargs.get("users")

        del kwargs["latency"]
        del kwargs["users"]
        del kwargs["additional_cooldown"]

        super().__init__(*args, **kwargs)

    async def request(self, method: str, url: str, **kwargs: Any) -> ClientResponse:
        """
        The request function is a wrapper around the ClientSession.request function,
        which handles ratelimits and other exceptions that may occur during requests.
        It also adds an additional cooldown to the Retry-After header value.

        :param method: Determine the type of request
        :param url: Specify the url that you want to make a request to
        :param **kwargs: Pass in additional parameters to the request function
        """

        response = await super().request(method=method, url=url, **kwargs)
        headers: Optional[dict] = kwargs.get("headers")

        token: Optional[str] = None  # pyright: ignore
        if headers:
            token: Optional[str] = headers.get("authorization")

        if response and token:
            try:
                _json: dict = await response.json()
            except client_exceptions.ContentTypeError:
                _json: dict = {}

            if isinstance(_json, dict):
                message: Optional[str] = _json.get("message")
                if message and "You need to verify" in message:
                    if self.users:
                        for user in self.users:
                            if user.token == token:
                                self.logger.error(f"It seems that your account has been blocked.\n-> Account: {user}")
                        response.status = 901

        if response.headers.get("Retry-After"):

            seconds = int(response.headers.get("Retry-After")) + self.ratelimit_additional_cooldown  # pyright: ignore
            if self.logger_status:
                self.logger.warning(f"Ratelimit has been reached. Awaiting {seconds} seconds before next request.")

            await sleep(seconds)
        else:
            await sleep(self.request_latency)

        return response


class HTTPClient:
    """
    HTTPClient handles all requests related to the client.
    It also has methods from checking tokens or creating a new session.

    :param api_version: version of the discord api used by the client
    :param loop: Set the event loop that will be used by the client
    :param logger: Enable/disable the logger
    :param request_latency: Control the rate of requests sent to discord
    :param ratelimit_additional_cooldown: Add a cooldown to the ratelimit
    """

    def __init__(
            self,
            api_version: API_VERSION,
            loop: Union[AbstractEventLoop, None],
            logger: bool,
            request_latency: float,
            ratelimit_additional_cooldown: float,
            client: Client,
            activity: Optional[ActivityBuilder]
    ):

        if api_version not in (9, 10):
            raise UnSupportedApiVersion

        self.request_latency: float = request_latency
        self.ratelimit_additional_cooldown: float = ratelimit_additional_cooldown

        self.api_version: int = api_version
        self.endpoint: str = Discord.ENDPOINT.value.format(self.api_version)
        self.endpoint_gateway: str = Discord.ENDPONT_GATEWAY.value.format(self.api_version)

        self.loop: AbstractEventLoop = loop if loop else get_event_loop()

        self._tokens: Union[str, list, None] = None
        self._logger_status: bool = logger

        self.logger: Logger.logger = Logger().logger  # pyright: ignore
        self.logger._status = self._logger_status
        self.session: Union[CustomSession, None] = None  # pyright: ignore

        self.users: list[UserClient] = []
        self.loop.run_until_complete(self.create_session())

        self.gateway: Gateway = Gateway(client=client, gateway_url=self.endpoint_gateway, activity=activity)

    async def create_session(self) -> None:
        """
        The create_session function is used to create a new session for the Client.
        The session object contains all of the information that we need in order to connect with Discord's API.
        """

        self.session: CustomSession = CustomSession(self.logger,
                                                    latency=self.request_latency,
                                                    additional_cooldown=self.ratelimit_additional_cooldown,
                                                    users=self.users)

    def _check_tokens(self, tokens: Union[list[str], str]) -> None:  # pyright: ignore
        """
        The _check_tokens function is used to check if the tokens provided are valid.
        If they are, then it will add them to the users list. If not, then it will delete them from the list.

        :param tokens: Tokens to check
        """

        async def _check() -> None:
            _url: str = self.endpoint + "users/@me"
            for token in tokens:
                header: AUTH_HEADER = AUTH_HEADER(authorization=token)
                response: ClientResponse = await self.session.get(_url, headers=header)
                if response.status != 200:
                    if self._logger_status:
                        self.logger.warning(
                            f"An invalid token has been provided: {token} | The token will be automatically deleted")

                else:
                    data: dict = await response.json()
                    data["token"] = token
                    data["endpoint"] = self.endpoint
                    data["endpoint_gateway"] = self.endpoint_gateway

                    self.users.append(UserClient(data, self.session))

            if self._logger_status:
                self.logger.info(f"Checking of tokens successfully completed | Loaded ({len(self.users)}) tokens\n")

        if not isinstance(tokens, list) and not isinstance(tokens, str):
            raise UnSupportedTokenType

        if isinstance(tokens, str):
            tokens: list[str] = [tokens]  # pyright: ignore

        self.loop.run_until_complete(_check())

    def __del__(self) -> None:
        try:
            self.loop.run_until_complete(self.session.close())
        except AttributeError:
            pass

    def run_async(self, function: Awaitable) -> None:
        """
        The run_async function is a helper function that allows you to run an asyncio coroutine in the background.
        It takes a single argument, which must be an awaitable object (such as a coroutine). It runs the event loop until
        the awaitable completes. This is useful for running tasks in parallel with other code.

        :param function: Specify the coroutine
        """

        self.loop.run_until_complete(function)

    async def request(self, url: str, method: METHOD, headers: Optional[dict] = None,
                      data: Optional[dict] = None) -> ClientResponse:
        """
        The request function is used to send a request to the API.

        :param url: Specify the url of the request
        :param method: Specify the type of request being sent
        :param headers: Pass in a dictionary of headers to be sent with the request
        :param data: Send data to the api
        """

        if method not in ("POST", "GET", "DELETE", "PATCH", "PUT"):
            raise InvalidMethodType(method)

        _url: str = self.endpoint + url

        if self._logger_status:
            self.logger.debug(f"Sending request: {method} -> {_url}")

        response: ClientResponse = await self.session.request(method=method, url=_url, headers=headers, json=data)
        print(await response.json())
        response.raise_for_status()

        return response
