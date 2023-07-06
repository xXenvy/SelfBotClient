from __future__ import annotations

from typing import Optional, Callable, TYPE_CHECKING
from asyncio import iscoroutinefunction

from .response import GatewayResponse
from .errors import FunctionIsNotCoroutine
from .enums import Events
from ..cache import CacheEventHandler

if TYPE_CHECKING:
    from ..user import UserClient
    from ..client import Client
    from .gateway import Gateway, GatewayConnection


class EventHandler:
    """
    EventHanlder is responsible for handling all evnets with :class:`Events`

    :param response: Get the event name and data
    :param kwargs: Pass in the user, client and gateway objects
    """
    def __init__(self, response: GatewayResponse, **kwargs):

        self.response: GatewayResponse = response

        self.user: UserClient = kwargs["user"]
        self.client: Client = kwargs["client"]
        self.gateway: Gateway = kwargs["gateway"]
        self.connection: GatewayConnection = kwargs["connection"]

        self.event_name: str = self.reformat_event_name(
            event_name=response.event_name
        )  # pyright: ignore

        self.available_events: dict[str, tuple] = {
        }  # Format: "Event name": (default_callback, *args)

        for event in Events:
            func = getattr(self.client, event.value)

            if event.name == "READY":
                args: tuple = (func, self.user)
            else:
                args: tuple = (func, self.user, self.response.data)

            self.available_events[event.value] = args

    async def handle_abstract_events(self):
        if self.response.op == 10:
            latency: int = self.response.data["heartbeat_interval"] / 1000
            self.connection._pulse = latency
            await self.connection.login()
            await self.connection.begin_presence()

        elif self.response.event_name == "GUILD_MEMBER_LIST_UPDATE":

            if self.response.data["ops"][0]["op"] == "SYNC" and self.connection.func:
                self.connection._times = 0
                await self.connection.func(self.response.data, self.connection._func_limit)

            elif self.response.data["ops"][0]["op"] == "INVALIDATE":
                self.connection._times += 1
                if self.connection._times >= 5:
                    self.connection._times = 0
                    self.connection.func = None
                    self.user._members_end = False

        else:
            if self.connection.func:
                await self.connection.func(self.response.data)
                self.connection.func = None

    async def handle_event(self) -> bool:
        """
        The handle_event function is responsible for handling the event that was received from the gateway.
        It will first check if there is a custom event handler registered in the events dictionary of your client,
        and if so, it will call that function with any arguments passed to it.
        If no custom event handler exists, then it will call the default one provided by :class:`Client`
        """

        cache_stuff: CacheEventHandler = CacheEventHandler(self.response, self.user)
        cache_stuff.handle_cache()

        event_args: Optional[tuple] = None

        if self.event_name in ("on_message_edit", "on_channel_edit", "on_guild_update"):
            event_args = cache_stuff.get_args()

            if not event_args:
                return False

        if not self.available_events.get(self.event_name):
            return False

        event_callback: Optional[Callable] = self.gateway.events.get(self.event_name)  # pyright: ignore

        default_event_callback: Optional[Callable] = self.available_events[self.event_name][0]  # pyright: ignore
        if not event_args:
            event_args: Optional[tuple] = self.available_events[self.event_name][1::]  # pyright: ignore

        if event_callback:
            self.client.loop.create_task(
                event_callback(*event_args) if event_args else event_callback()
            )
        else:
            if iscoroutinefunction(default_event_callback):
                self.client.loop.create_task(
                    default_event_callback(*event_args) if event_args else default_event_callback()
                )
            else:
                raise FunctionIsNotCoroutine(default_event_callback)

        return True

    @staticmethod
    def reformat_event_name(event_name: Optional[str]) -> Optional[str]:
        """
        The reformat_event_name function takes in an event name and returns the corresponding value of that event.
        If no event is found, it will return a space.

        :param event_name: Specify the event_name
        """

        for event in Events:
            if event.name == event_name:
                event_name = event.value

        if not event_name:
            return " "

        return event_name
