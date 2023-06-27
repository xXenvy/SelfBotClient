from __future__ import annotations

from typing import List, Optional, Any, Callable, TYPE_CHECKING
from .response import GatewayResponse
from .errors import FunctionIsNotCoroutine

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
            "on_ready": (self.client.on_ready, self.user),
            "on_message_create": (self.client.on_message_create, self.user, self.response.data),
            "on_message_delete": (self.client.on_message_delete, self.user, self.response.data),
            "on_message_edit": (self.client.on_message_edit, self.user, self.response.data)
        }  # Format: "Event name": (default_callback, *args)

    async def handle_event(self) -> bool:
        if not self.gateway.events.get(self.event_name):
            return False
        if not self.available_events.get(self.event_name):
            return False

        event_callback: Optional[Callable] = self.gateway.events[self.event_name]  # pyright: ignore

        default_event_callback: Optional[Callable] = self.available_events[self.event_name][0]  # pyright: ignore
        event_args: Optional[tuple] = self.available_events[self.event_name][1::]  # pyright: ignore

        if event_callback:
            await event_callback(*event_args) if event_args else await event_callback()
        else:
            if iscoroutinefunction(default_event_callback):
                await default_event_callback(*event_args) if event_args else await default_event_callback()
            else:
                raise FunctionIsNotCoroutine(default_event_callback)

        return True

    @staticmethod
    def reformat_event_name(event_name: Optional[str]) -> Optional[str]:
        events_formats: dict[str, str] = {
            "READY": "on_ready",
            "MESSAGE_CREATE": "on_message_create",
            "MESSAGE_DELETE": "on_message_delete",
            "MESSAGE_UPDATE": "on_message_edit"
        }

        if not event_name or not events_formats.get(event_name):
            return " "

        return events_formats[event_name]
