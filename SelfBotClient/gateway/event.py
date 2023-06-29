from __future__ import annotations

from typing import List, Optional, Callable, TYPE_CHECKING
from .response import GatewayResponse
from .errors import FunctionIsNotCoroutine
from .enums import Events

if TYPE_CHECKING:
    from ..user import UserClient
    from ..client import Client
    from .gateway import Gateway

from asyncio import Task, iscoroutinefunction


class EventHandler:

    def __init__(self, response: GatewayResponse, **kwargs):

        self.response: GatewayResponse = response

        self.user: UserClient = kwargs["user"]
        self.client: Client = kwargs["client"]
        self.gateway: Gateway = kwargs["gateway"]

        self.event_name: str = self.reformat_event_name(
            event_name=response.event_name
        )  # pyright: ignore

        self.available_events: dict[str, tuple] = {
        }  # Format: "Event name": (default_callback, *args)

        for event in Events:
            func = getattr(self.client, event.value)
            args = (func, self.user, self.response.data) if event.name != "READY" else (func, self.user)
            self.available_events[event.value] = args

    async def handle_event(self) -> bool:
        if not self.available_events.get(self.event_name):
            return False

        event_callback: Optional[Callable] = self.gateway.events.get(self.event_name)  # pyright: ignore

        default_event_callback: Optional[Callable] = self.available_events[self.event_name][0]  # pyright: ignore
        event_args: Optional[tuple] = self.available_events[self.event_name][1::]  # pyright: ignore
        task: Optional[Task] = None

        if event_callback:
            task: Optional[Task] = self.client.loop.create_task(
                event_callback(*event_args) if event_args else event_callback()
            )
        else:
            if iscoroutinefunction(default_event_callback):
                task: Optional[Task] = self.client.loop.create_task(
                    default_event_callback(*event_args) if event_args else default_event_callback()
                )
            else:
                raise FunctionIsNotCoroutine(default_event_callback)

        if task:
            await task

        return True

    @staticmethod
    def reformat_event_name(event_name: Optional[str]) -> Optional[str]:
        for event in Events:
            if event.name == event_name:
                event_name = event.value

        if not event_name:
            return " "

        return event_name
