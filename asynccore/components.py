from __future__ import annotations

from typing import Optional, TYPE_CHECKING, Union

from random import choice
from string import ascii_letters, digits
from time import time

from .enums import Components
from .typings import AUTH_HEADER

if TYPE_CHECKING:
    from .client import Client
    from .user import UserClient
    from . import ClientResponse

__all__: tuple[str, str, str] = (
    "Button",
    "MessageComponents",
    "SelectMenu"
)


class SelectMenu:

    def __init__(self, data: dict, application_id: int):
        self._data: dict = data

        self.application_id: int = application_id
        self.type: int = self._data["type"]
        self.placeholder: str = self._data["placeholder"]
        self.custom_id: Optional[str] = self._data.get("custom_id")
        self.max_values: int = self._data["max_values"]
        self.min_values: int = self._data["min_values"]

        self.options: Optional[list[dict]] = self._data.get("options")
        # Options are only available for SelectMenu with type 3

    async def use(self, client: Client, user: UserClient, channel_id: int, message_id: int,
                  guild_id: int, message_flags: int, values: list[Union[str, int]]) -> Optional[ClientResponse]:

        """
        Use this function to send values in SelectMenu


        :param client: Client to make the request to discord
        :param user: User to send SelectMenu
        :param channel_id: Specify the channel id of the message that triggered this interaction
        :param message_id: Identify the message that the reaction was added to
        :param guild_id: Identify the guild that the message is in
        :param message_flags: Pass messages flags
        :param values: Pass the values of the fields in select menu

        .. note::
            For SelectMenu with roles, users, etc. The value parameter must be the id of the specified object.
        """

        session_id: str = "".join(choice(ascii_letters + digits) for _ in range(32))
        nonce = str((int(time()) * 1000 - 1420070400000) * 4194304)

        data: dict = {
            "component_type": self.type,
            "custom_id": self.custom_id,
            "type": self.type,
            "values": values
        }

        payload: dict = {
            "type": 3,
            "nonce": nonce,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message_flags": message_flags,
            "message_id": message_id,
            "application_id": self.application_id,
            "data": data,
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
        return f"<SelectMenu(placeholder={self.placeholder}, custom_id={self.custom_id})>"


class Button:
    """
    The Button class is responsible for interacting with the button

    :param data: Store the data of the button
    """

    def __init__(self, data: dict, application_id: int):
        self._data: dict = data

        self.application_id: int = application_id
        self.label: Optional[str] = self._data.get("label")
        self.custom_id: Optional[str] = self._data.get("custom_id")

    async def use(self, client: Client, user: UserClient, channel_id: int, message_id: int,
                  guild_id: int, message_flags: int) -> Optional[ClientResponse]:
        """
        The use function allows you to press a button

        :param client: Client needed to send a request
        :param user: User who is supposed to send a request who presses the button
        :param channel_id: Specify the channel id of the message that contains the button
        :param message_id: Identify the message that contains the button
        :param guild_id: Identify the guild that the message is in
        :param message_flags: Determine message flags
        """

        session_id: str = "".join(choice(ascii_letters + digits) for _ in range(32))
        nonce = str((int(time()) * 1000 - 1420070400000) * 4194304)

        payload: dict = {
            "type": 3,
            "nonce": nonce,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "message_flags": message_flags,
            "message_id": message_id,
            "application_id": self.application_id,
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
    """
    The object is responsible for storing message components and returning them.

    :param message_components: List with data of message components
    """

    def __init__(self, application_id: int, message_components: list[dict]):
        self.types = Components
        self.application_id: int = application_id
        self.components: Optional[list[dict]] = None

        if isinstance(message_components, list):
            self.components: Optional[list[dict]] = message_components
        else:
            raise TypeError("Message components must be list[dict] type")

    def _find_buttons(self) -> list[Optional[Button]]:
        """
        The _find_buttons function is a helper function that finds all the buttons in a message.
        It returns a list of Button objects, which are defined in the Button class.
        """

        if not self.components:
            raise ValueError("Missing message components")

        buttons: list[Optional[Button]] = []

        for component in self.components:
            for _comp_data in component["components"]:
                if _comp_data["type"] == self.types.BUTTON.value:
                    buttons.append(Button({"component_type": 2, "custom_id": _comp_data.get("custom_id"),
                                           "label": _comp_data["label"]}, self.application_id))
        return buttons

    def _find_selectmenus(self) -> list[Optional[SelectMenu]]:
        """
        The _find_buttons function is a helper function that finds all the select menus in a message.
        It returns a list of SelectMenu objects, which are defined in the SelectMenu class.
        """

        if not self.components:
            raise ValueError("Missing message components")

        selectmenus: list[Optional[SelectMenu]] = []

        for component in self.components:
            for component_data in component["components"]:
                if component_data["type"] >= self.types.DROPDOWN.value:
                    selectmenus.append(SelectMenu(component_data, self.application_id))

        return selectmenus

    def get_buttons(self) -> list[Optional[Button]]:
        """
        The get_buttons function returns a list of Button objects.
        """

        buttons = self._find_buttons()

        return buttons

    def get_selectmenus(self) -> list[Optional[SelectMenu]]:

        menus = self._find_selectmenus()
        return menus
