from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable
from time import time

from json import dumps
from asyncio import AbstractEventLoop, sleep, Queue, create_task, gather, Task, iscoroutinefunction
import socket
from websockets import connect, WebSocketClientProtocol, ConnectionClosed  # pyright: ignore

from .response import GatewayResponse
from .errors import MissingEventName, InvalidEventName, FunctionIsNotCoroutine
from .event import EventHandler
from .enums import Events

if TYPE_CHECKING:
    from ..client import Client
    from ..user import UserClient
    from ..activity import ActivityBuilder


def parametrized(decorator):
    def layer(*args, **kwargs):
        def repl(function):
            self = args[0]
            return decorator(self, function, **kwargs)

        return repl

    return layer


class Gateway:
    """
    The gateway class is responsible for connecting all users to the discord's gateway.

    :param client: Library main client
    :param gateway_url: gateway_url to connect to the discord gateway
    :param activity: Set the activity of the user
    """

    def __init__(self, client: Client, gateway_url: str, activity: Optional[ActivityBuilder]):

        self.client: Client = client
        self.gateway_url: str = gateway_url
        self.activity = activity

        self.events: dict[str, Callable] = {}

        self.supportted_events: list[str] = [event.value for event in Events]

    def run(self, reconnect: bool = False):
        """
        Main method of the class. Starts the users' gateways

        :param reconnect: Determine if the user should reconnect to the server or not
        """

        self.__start(reconnect)

    def __start(self, reconnect: bool):
        """
        The __start function creates GatewayConnection objects for each user in the client's users list.
        It then runs the run function of each GatewayConnection object asynchronously.

        :param reconnect: Determine whether or not the connection is a reconnection
        """

        tasks: list[Task] = []

        for user in self.client.users:
            connection = GatewayConnection(client=self.client, user=user,
                                           gateway=self, activity=self.activity,
                                           reconnect=reconnect)

            task: Task = self.client.loop.create_task(connection.run(self.gateway_url))
            tasks.append(task)

        async def run():
            await gather(*tasks)

        self.client.loop.run_until_complete(run())

    @parametrized
    def event(self, function: Callable, **kwargs):
        """
        The event function is used to register a function as an event.

        :param function: function to register
        :param kwargs: Pass a dictionary of arguments to the function
        """

        if callable(function):
            name = kwargs.get("event_name")
            if not name:
                raise MissingEventName(function)

            if name in self.supportted_events:
                if iscoroutinefunction(function):
                    self.events[name] = function

                else:
                    raise FunctionIsNotCoroutine(function)
            else:
                raise InvalidEventName(name)


class GatewayConnection:
    """
    GatewayConnection is responsible for communication between the discord gateway and the user

    :param client: Store the client object in the gateway connection
    :param user: Store the user object in the gateway connection,
    :param gateway: Create a new gateway connection
    :param activity: Set the activity of the user
    :param reconnect: Determine whether the userx should reconnect or not
    """

    def __init__(self, client: Client, user: UserClient, gateway: Gateway,
                 activity: Optional[ActivityBuilder], reconnect: bool):

        self.client: Client = client
        self.user: UserClient = user
        self.activity: Optional[ActivityBuilder] = activity
        self.reconnect: bool = reconnect

        self._gateway: Gateway = gateway
        self._loop: AbstractEventLoop = client.loop
        self._pulse: int = 5
        self._queue: Queue = Queue()
        self._last_sequence: int = 0
        self._resume_gateway: Optional[str] = None
        self._session_id: Optional[str] = None

        self.user.gateway_connection = self

        self.func: Optional[Callable] = None
        self._times: int = 0
        self._func_limit: Optional[int] = None

        self.websocket: WebSocketClientProtocol = None

    async def run(self, gateway_url: str) -> None:
        """
        The run function is the main function of the Gateway class.
        It connects to a gateway, and then creates three tasks:
            1) Receiving responses from Discord (self._receive_response())
            2) Sending requests to Discord (self._send_request())
            3) Pinging Discord every x seconds (self._ping_loop())

        :param gateway_url: url to connect
        """

        try:
            async with connect(gateway_url, extra_headers=self.get_headers) as websocket:
                self.websocket: WebSocketClientProtocol = websocket

                if self.client.logger._status:
                    self.client.logger.info(f"Successfully connected to {gateway_url}")

                tasks: list[Task] = [
                    create_task(self._receive_response()),
                    create_task(self._send_request()),
                    create_task(self._ping_loop())]

                for task in tasks:
                    await task

        except ConnectionClosed:
            if self.client.logger._status:
                self.client.logger.error(f"Connection: {self._gateway.gateway_url} Closed. Trying to resume.")

            if not self._resume_gateway or not self._session_id or not self.reconnect:
                return

            await self.resume()

    async def resume(self):
        """
        The resume function is used to resume a connection that has been closed.
        It will attempt to reconnect every second until the websocket is open again.
        """

        while not self.websocket.open:
            await sleep(1)
            await self.resume_connection()

    async def resume_connection(self):
        """
        The resume_connection function is used to resume a connection with the Discord Gateway.
        It does this by sending a RESUME payload to the gateway.
        """

        try:
            async with connect(self._resume_gateway, extra_headers=self.get_headers) as websocket:
                self.websocket: WebSocketClientProtocol = websocket

                if self.client.logger._status:
                    self.client.logger.info(f"Successfully connected to: {self._resume_gateway}")

                tasks: list[Task] = [
                    create_task(self._send_resume()),
                    create_task(self._receive_response()),
                    create_task(self._send_request()),
                    create_task(self._ping_loop())]

                for task in tasks:
                    await task
        except socket.gaierror:
            pass

        except ConnectionClosed:
            if not self._resume_gateway or not self._session_id:
                return

            if self.client.logger._status:
                self.client.logger.error(f"Connection: {self._gateway.gateway_url} Closed. Trying to resume.")

            await self.resume()

    @property
    def get_headers(self) -> dict:
        """
        The get_headers function returns a dictionary of headers that are used to make the request.
        """

        headers = {
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
            "Sec-WebSocket-Extensions": "permessage-deflate; client_max_window_bits",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0"
        }
        return headers

    async def begin_presence(self):
        """
        The begin_presence function is used to send the initial presence payload to Discord.
        This function is called when the client connects and has received a READY payload from Discord.
        The begin_presence function will only be called if an activity was set on the client before connecting.
        """

        if self.activity:
            payload = {
                "op": 3,
                "d": {
                    "since": time(),
                    "activities": [{
                        "name": self.activity.activity_name,
                        "type": self.activity.activity_type,
                        "created_at": time(),
                        "since": 0,
                        "details": self.activity.activity_details
                    }],
                    "status": self.activity.user_status,
                    "afk": False,
                }
            }
            await self.send(payload)

    async def login(self) -> None:
        """
        The login function is used to send the login request to Discord.
        It takes no arguments, and returns nothing.
        """

        os: str = "Windows Desktop"
        browser: str = "Chrome"
        device: str = "Windows"

        if self.activity:
            if self.activity.user_platform.lower() == "android":
                os: str = self.activity.user_platform
                browser: str = f"Discord {os}"
                device: str = f"Discord {os}"

        request = {
            "op": 2,
            "d": {
                "token": self.user.token,
                "capabilities": 4093,
                "properties": {
                    "os": os,
                    "browser": browser,
                    "device": device
                },
                "compress": False
            },
            "intents": 98047
        }
        await self.send(request)

    async def _receive_response(self):
        """
        The _receive_response function is a coroutine that receives responses from the gateway.
        It handles all events and dispatches them to their respective handlers. It also handles
        the heartbeat interval, which is used to keep the connection alive.
        """

        async for response in self.websocket:
            gateway_response: GatewayResponse = GatewayResponse(response, self.user)

            if isinstance(gateway_response.data, dict):
                if gateway_response.data.get("session_id"):
                    self._session_id = gateway_response.data.get("session_id")

            if gateway_response.sequence:
                self._last_sequence = gateway_response.sequence

            if gateway_response.event:
                if gateway_response.event_name == "READY":
                    if self.func:
                        continue

                    self._resume_gateway = gateway_response.data.get("resume_gateway_url")

            handler = EventHandler(
                response=gateway_response,
                client=self.client,
                user=self.user,
                gateway=self._gateway,
                connection=self
            )

            def check_event_type():
                return gateway_response.event_name in ("GUILD_APPLICATION_COMMANDS_UPDATE",
                                                       "GUILD_MEMBER_LIST_UPDATE") or gateway_response.op == 10

            if check_event_type():
                await handler.handle_abstract_events()
            else:
                await handler.handle_event()

    async def _send_request(self):
        """
        The _send_request function is a coroutine that sends requests to the server.
        It does this by waiting for a request to be added to the queue, then sending it
        to the websocket. It waits 0.1 seconds before sending another request.
        """

        while True:
            request: Optional[dict] = await self._queue.get()
            _request: str = dumps(request)
            await self.websocket.send(_request)
            await sleep(0.1)

    async def _ping_loop(self):
        """
        The _ping_loop function is a coroutine that runs in the background of the client.
        It sends a ping request to Discord every self._pulse seconds, which is set to 5 by default.
        The purpose of this function is to keep the connection alive and prevent it from timing out.
        """

        while True:
            await sleep(self._pulse)

            ping_request: dict = {
                "op": 1,
                "d": time()
            }

            await self.send(ping_request)

    async def _send_resume(self):
        """
        The _send_resume function is used to send a resume payload to the Discord gateway.
        This function is called when the websocket connection has been lost and needs to be re-established.
        The payload contains information about the user's session, including their token, session ID, and last sequence.
        """

        payload: dict = {
            "op": 6,
            "d": {
                "token": self.user.token,
                "session_id": self._session_id,
                "seq": self._last_sequence
            }
        }
        await self.send(payload)

    async def send(self, request):
        """
        The send function is a coroutine that takes in a request and puts it into the queue.
        """
        await self._queue.put(request)

    async def application_update_request(self, request: dict, func: Callable, limit: Optional[int] = None):
        """
        The application_update_request function is a coroutine that takes in a request and function.
        The request is put into the queue, and the function is set to be called when it's time to process
        the request.

        :param request: Pass the request to the application_update_request function
        :param func: Store the function that will be called when a response is received

        .. note::
            This is mainly used for .search_slash_commands method
        """

        self.func: Optional[Callable] = func
        self._func_limit: Optional[int] = limit
        await self._queue.put(request)
