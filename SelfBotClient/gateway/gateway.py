from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable, Coroutine
from websockets import connect, WebSocketClientProtocol, ConnectionClosed, exceptions  # pyright: ignore

if TYPE_CHECKING:
    from ..client import Client
    from ..user import UserClient
    from ..presence import ActivityBuilder

from .response import GatewayResponse, dumps
from .errors import MissingEventName, InvalidEventName, FunctionIsNotCoroutine
from .event import EventHandler
from .enums import Events

from asyncio import AbstractEventLoop, sleep, Queue, create_task, gather, Task, iscoroutinefunction
from time import time


def parametrized(decorator):
    def layer(*args, **kwargs):

        def repl(f):
            self = args[0]
            return decorator(self, f, **kwargs)

        return repl

    return layer


class Gateway:

    def __init__(self, client: Client, gateway_url: str, activity: Optional[ActivityBuilder]):
        self.client: Client = client
        self.gateway_url: str = gateway_url
        self.activity = activity

        self.events: dict[str, Callable] = {}

        self.supportted_events: list[str] = [event.value for event in Events]

    def run(self):
        users_gateways = UsersGateways(self.client, self.gateway_url, self, self.activity)
        users_gateways.start()

    @parametrized
    def event(self, function: Coroutine, **kwargs):

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


class UsersGateways:

    def __init__(self, client: Client, gateway_url: str, gateway: Gateway, activity: Optional[ActivityBuilder]):
        self.client: Client = client
        self.gateway_url: str = gateway_url
        self.gateway: Gateway = gateway
        self.activity = activity

    def start(self):
        tasks: list[Task] = []
        for user in self.client.users:
            connection = GatewayConnection(client=self.client, user=user,
                                           gateway=self.gateway, activity=self.activity)

            task: Task = self.client.loop.create_task(connection.run(self.gateway_url))
            tasks.append(task)

        async def run():
            await gather(*tasks)

        self.client.loop.run_until_complete(run())


class GatewayConnection:

    def __init__(self, client: Client, user: UserClient, gateway: Gateway, activity: Optional[ActivityBuilder]):
        self.client: Client = client
        self.user: UserClient = user
        self.activity: Optional[ActivityBuilder] = activity

        self._gateway: Gateway = gateway
        self._loop: AbstractEventLoop = client.loop
        self._pulse: int = 5
        self._queue: Queue = Queue()

        self.user.gateway_connection = self
        self.func: Optional[Callable] = None

        self.websocket: WebSocketClientProtocol = None

    async def run(self, gateway_url: str):
        try:
            async with connect(gateway_url, extra_headers=self.get_headers) as websocket:
                self.websocket: WebSocketClientProtocol = websocket

                tasks: list[Task] = [
                    create_task(self._receive_response()),
                    create_task(self._send_request()),
                    create_task(self._ping_loop())]

                await gather(*tasks, return_exceptions=True)
        except ConnectionClosed:
            exit("Connection closed.")

    @property
    def get_headers(self) -> dict:
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

    async def login(self):
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
        async for response in self.websocket:
            gateway_response: GatewayResponse = GatewayResponse(response, self.user)
            if gateway_response.event:
                if gateway_response.event_name == "GUILD_APPLICATION_COMMANDS_UPDATE" and self.func:

                    await self.func(gateway_response.data)
                    self.func: Optional[Callable] = None

                handler = EventHandler(
                    response=gateway_response,
                    client=self.client,
                    user=self.user,
                    gateway=self._gateway
                )
                await handler.handle_event()

            if gateway_response.op == 10:
                latency: int = gateway_response.data["heartbeat_interval"] / 1000
                self._pulse: int = latency
                await self.login()
                await self.begin_presence()

    async def _send_request(self):
        while True:
            request: Optional[dict] = await self._queue.get()
            _request: str = dumps(request)
            await self.websocket.send(_request)

            await sleep(0.5)

    async def _ping_loop(self):
        while True:
            await sleep(self._pulse)

            ping_request: dict = {
                "op": 1,
                "d": time()
            }

            await self.send(ping_request)

    async def send(self, request):
        await self._queue.put(request)

    async def application_update_request(self, request: dict, func: Callable):
        self.func: Optional[Callable] = func
        await self._queue.put(request)
