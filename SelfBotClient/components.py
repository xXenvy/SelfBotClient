from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client
    from .user import UserClient
    from . import ClientResponse

from .enums import Components
from .typings import AUTH_HEADER

from random import choice
from string import ascii_letters, digits
from time import time


__all__: tuple[str, str] = (
    "Button",
    "MessageComponents"
)


class Button:

    def __init__(self, data: dict):
        self._data: dict = data

        self.label: Optional[str] = self._data.get("label")
        self.custom_id: Optional[str] = self._data.get("custom_id")

    async def click(self, client: Client, user: UserClient, application_id: int, channel_id: int,
                    message_id: int, guild_id: int, message_flags: int) -> Optional[ClientResponse]:

        session_id: str = "".join(choice(ascii_letters + digits) for _ in range(32))
        nonce = str((int(time()) * 1000 - 1420070400000) * 4194304)

        payload: dict = {
            "type": 3,
            "nonce": nonce,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message_flags": message_flags,
            "message_id": message_id,
            "application_id": application_id,
            "data": self._data,
            "session_id": session_id
        }

        headers: dict = AUTH_HEADER(authorization=user.token)  # pyright: ignore

        response: ClientResponse = await client.request(
            url="interactions",
            method="POST",
            data=payload,
            headers=headers
        )
        return response

    def __repr__(self):
        return f"<Button(label={self.label}, custom_id={self.custom_id})>"


class MessageComponents:

    def __init__(self, message_components: list[dict]):
        self.types = Components
        self.components: Optional[list[dict]] = None

        if isinstance(message_components, list):
            self.components: Optional[list[dict]] = message_components
        else:
            raise TypeError("Message components must be list[dict] type")

    def _find_buttons(self) -> list[Optional[Button]]:
        if not self.components:
            raise ValueError("Missing message components")

        buttons: list[Optional[Button]] = []

        for component in self.components:
            for _comp_data in component["components"]:
                if _comp_data["type"] == self.types.BUTTON.value:
                    buttons.append(Button({"component_type": 2, "custom_id": _comp_data.get("custom_id"),
                                           "label": _comp_data["label"]}))
        return buttons

    def get_buttons(self) -> list[Optional[Button]]:
        buttons = self._find_buttons()

        return buttons

