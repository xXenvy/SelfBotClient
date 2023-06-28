from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Callable, Coroutine
from websockets import connect, WebSocketClientProtocol, ConnectionClosed, exceptions  # pyright: ignore

if TYPE_CHECKING:
    from ..client import Client
    from ..user import UserClient

from .response import GatewayResponse, dumps
from .errors import MissingEventName, InvalidEventName, FunctionIsNotCoroutine
from .event import EventHandler
from .enums import Events

from threading import Thread
from asyncio import AbstractEventLoop, sleep, Queue, create_task, gather, Task, iscoroutinefunction, run_coroutine_threadsafe
from time import time


def parametrized(decorator):
    def layer(*args, **kwargs):

        def repl(f):
            self = args[0]
            return decorator(self, f, **kwargs)

        return repl

    return layer


class Gateway:

    def __init__(self, client: Client, gateway_url: str):
        self.client: Client = client
        self.gateway_url: str = gateway_url

        self.events: dict[str, Callable] = {

        }

        self.supportted_events: list[str] = [event.value for event in Events]

    def run(self):
        users_gateways = UsersGateways(self.client, self.gateway_url, self)
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

    def __init__(self, client: Client, gateway_url: str, gateway: Gateway):
        self.client: Client = client
        self.gateway_url: str = gateway_url
        self.gateway: Gateway = gateway

    def start(self):
        tasks: list[Task] = []
        for user in self.client.users:
            connection = GatewayConnection(client=self.client, user=user,
                                           gateway=self.gateway)

            self.client.loop.run_until_complete(connection.run(self.gateway_url))


class GatewayConnection:

    def __init__(self, client: Client, user: UserClient, gateway: Gateway):
        self.client: Client = client
        self.user: UserClient = user

        self._gateway: Gateway = gateway
        self._loop: AbstractEventLoop = client.loop
        self._pulse: int = 5
        self._queue: Queue = Queue()

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

    async def login(self):
        request = {
            "op": 2,
            "d": {
                "token": self.user.token,
                "capabilities": 4093,
                "properties": {
                    "os": "linux",
                    "browser": f"Chrome",
                    "device": f"Discord Windows"
                },
                "compress": False
            },
            "intents": 98047
        }
        await self._send(request)

    async def _receive_response(self):
        async for response in self.websocket:
            gateway_response: GatewayResponse = GatewayResponse(response, self.user)
            if gateway_response.event:

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

            await self._send(ping_request)

    async def _send(self, request):
        await self._queue.put(request)
