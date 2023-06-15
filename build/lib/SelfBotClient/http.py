from .typings import API_VERSION, AUTH_HEADER, METHOD
from .errors import UnSupportedApiVersion, UnSupportedTokenType, InvalidMethodType
from .enums import Discord
from .logger import Logger
from .user import UserClient

from typing import Union, Awaitable, Any
from aiohttp import ClientSession, ClientResponse, client_exceptions
from asyncio import AbstractEventLoop, sleep, get_event_loop


class CustomSession(ClientSession):

    def __init__(self, logger: Logger, *args: Any, **kwargs: Any):
        """
        The __init__ function is called when the class is instantiated.
        It sets up all of the variables that are needed for other functions to work properly.
        The super() function calls __init__ from the parent class, which in this case is ClientSession.

        :param self: Represent the instance of the class
        :param logger: Logger: Pass the logger object to the class
        :param *args: Any: Pass any additional arguments to the superclass
        :param **kwargs: Any: Pass in additional parameters that are not explicitly defined
        :return: None
        """

        self.logger: Logger = logger
        self.logger_status = logger._status

        self.request_latency: float = kwargs.get("latency")
        self.ratelimit_additional_cooldown: float = kwargs.get("additional_cooldown")
        self.users: list[UserClient] = kwargs.get("users")

        del kwargs["latency"]
        del kwargs["users"]
        del kwargs["additional_cooldown"]

        super().__init__(*args, **kwargs)

    async def request(self, method: str, url: str, **kwargs: Any) -> ClientResponse:
        """
        The request function is a wrapper around the ClientSession.request function,
        which handles ratelimits and other exceptions that may occur during requests.
        It also adds an additional cooldown to the Retry-After header value.

        :param self: Represent the instance of the class
        :param method: str: Determine the type of request
        :param url: str: Specify the url that you want to make a request to
        :param **kwargs: Any: Pass in additional parameters to the request function
        :return: A clientresponse object
        """

        response = await super().request(method=method, url=url, **kwargs)

        headers: dict = kwargs.get("headers")
        if headers:
            token: str = headers.get("authorization")

        if response and headers:
            try:
                _json: dict = await response.json()
            except client_exceptions.ContentTypeError:
                _json: dict = {}
            if isinstance(_json, dict) and _json.get("message"):
                if "You need to verify" in _json.get("message"):
                    for user in self.users:
                        if user.token == token:
                            self.logger.error(f"It seems that your account has been blocked.\n-> Account: {user}")
                    response.status = 901

        if response.headers.get("Retry-After"):

            seconds = int(response.headers.get("Retry-After")) + self.ratelimit_additional_cooldown
            if self.logger_status:
                self.logger.warning(f"Ratelimit has been reached. Awaiting {seconds} seconds before next request.")

            await sleep(seconds)
        else:
            await sleep(self.request_latency)

        return response

    async def get(self, url: str, *, allow_redirects: bool = True, **kwargs: Any) -> ClientResponse:
        """
        The get function is a wrapper for the get function in the ClientSession class.
        It allows us to use asyncio's await syntax, which makes it easier to write asynchronous code.
        The get function takes a url and returns an object of type ClientResponse.

        :param self: Represent the instance of the class
        :param url: str: Specify the url to be requested
        :param *: Unpack the tuple and the ** parameter is used to unpack the dictionary
        :param allow_redirects: bool: Determine whether the client will follow redirects
        :param **kwargs: Any: Pass in any additional parameters that are not specified
        :return: A clientresponse object
        """

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
        """
        The __init__ function is called when the class is instantiated.
        It allows the class to initialize its attributes, and do any other necessary setup.
        The __init__ function can accept arguments, which will be passed on from the object creation.

        :param self: Represent the instance of the class
        :param api_version: API_VERSION: Set the api version of discord
        :param loop: AbstractEventLoop: Set the event loop that will be used by the client
        :param logger: bool: Enable/disable the logger
        :param request_latency: float: Control the rate of requests sent to discord
        :param ratelimit_additional_cooldown: float: Add a cooldown to the ratelimit
        :return: Nothing, so the return type is none
        """

        if api_version not in (9, 10):
            raise UnSupportedApiVersion

        self.request_latency: float = request_latency
        self.ratelimit_additional_cooldown: float = ratelimit_additional_cooldown

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

    async def create_session(self) -> None:
        """
        The create_session function is used to create a new session for the bot.
        This function is called when the bot starts up, and also when it needs to reconnect.
        The session object contains all of the information about how many requests have been made,
        and how long until more can be made.

        :param self: Refer to the current instance of a class
        :return: None
        """

        self.session: CustomSession = CustomSession(self.logger,
                                                    latency=self.request_latency,
                                                    additional_cooldown=self.ratelimit_additional_cooldown,
                                                    users=self.users)

    def _check_tokens(self) -> None:
        """
        The _check_tokens function is used to check if the tokens provided are valid.
        If a token is invalid, it will be removed from the list of tokens and not be used in any future requests.
        The function also creates UserClient objects for each valid token.

        :param self: Represent the instance of the class
        :return: None
        """

        async def _check(_type: Union[type[list], type[str]]) -> None:
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

    def __del__(self) -> None:
        """
        The __del__ function is called when the object is garbage collected.
        The __del__ function can be used to clean up resources that are not managed by Python, such as file handles or network connections.
        If you have a class with an open file handle, and you want to make sure that the file gets closed when the object gets deleted,
        you can implement __del__ for this purpose.

        :param self: Represent the instance of the class
        :return: None
        """
        try:
            self.loop.run_until_complete(self.session.close())
        except AttributeError:
            pass

    def run_async(self, function: Awaitable) -> None:
        """
        The run_async function is a helper function that allows you to run an asyncio coroutine in the background.
        It takes a single argument, which must be an awaitable object (such as a coroutine). It runs the event loop until
        the awaitable completes and then returns. This is useful for running tasks in parallel with other code.

        :param self: Access the attributes and methods of a class
        :param function: Awaitable: Specify the type of the parameter function
        :return: None
        """
        self.loop.run_until_complete(function)

    async def request(self, url: str, method: METHOD, headers: dict = None, data: dict = None) -> ClientResponse:
        """
        The request function is used to send a request to the API.

        :param self: Represent the instance of the class
        :param url: str: Specify the url of the request
        :param method: METHOD: Specify the type of request being sent
        :param headers: dict: Pass in a dictionary of headers to be sent with the request
        :param data: dict: Send data to the server
        :return: A clientresponse object
        """

        if method not in ("POST", "GET", "DELETE", "PATCH", "PUT"):
            raise InvalidMethodType(method)

        url: str = self.endpoint + url

        if self._logger_status:
            self.logger.debug(f"Sending request: {method} -> {url}")

        response: ClientResponse = await self.session.request(method=method, url=url, headers=headers, json=data)
        response.raise_for_status()

        return response
