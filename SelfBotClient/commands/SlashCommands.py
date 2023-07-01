from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any
from ..typings import AUTH_HEADER

from time import time
from random import choice
from string import ascii_letters, digits

if TYPE_CHECKING:
    from ..user import UserClient
    from ..client import Client, ClientResponse


class SlashCommand:

    def __init__(self, command_data: dict, client: Client):

        self.client: Client = client
        self.command_data: dict = command_data
        self.application_id: int = self.command_data["application_id"]
        self.command_name: str = self.command_data["name"]

        self.sub_command: Optional[str] = self.command_data.get("sub_command")
        self.global_name: Optional[str] = self.command_data.get("global_name")

    def __repr__(self):
        command_name = self.command_name if not self.global_name else self.global_name
        return f"<SlashCommand(name={command_name}, application_id={self.application_id})>"

    async def reformat_data(self, data: dict, nonce: str, inputs: Optional[dict[str, Any]] = None):

        new_data: dict = {}
        formatted_options: list[Optional[dict]] = []

        version: str = data["version"]
        id: str = data["id"]
        command_name: str = data["name"]
        command_type: int = data["type"]
        options: Optional[list[dict]] = data.get("options")

        if options:
            for option in options:
                if option["type"] == 3:  # Normal command with inputs
                    for key, value in option.items():
                        if key == "name":
                            for option_name, option_value in inputs.items():
                                if value == option_name:
                                    _type: int = option["type"]
                                    __option_data: dict = {
                                        "type": _type,
                                        "name": option_name,
                                        "value": option_value
                                    }
                                    formatted_options.append(__option_data)

                elif option["type"] == 1:  # Command with subcommands
                    option_inputs_list: list[dict] = []

                    if len(option["options"]) >= 1:
                        for __option in option["options"]:
                            for key, value in __option.items():
                                if key == "name":
                                    for input_name, input_value in inputs.items():
                                        if value == input_name:
                                            _type: int = __option["type"]
                                            __option_data: dict = {
                                                "type": _type,
                                                "name": input_name,
                                                "value": input_value
                                            }
                                            option_inputs_list.append(__option_data)

                    option_data: dict = {
                        "type": command_type,
                        "name": option["name"],
                        "options": option_inputs_list
                    }
                    formatted_options.append(option_data)

        default_member_permissions = self.command_data["default_member_permissions"]
        nsfw: bool = self.command_data["nsfw"]
        command_description: str = self.command_data["description"]
        dm_permissions: bool = self.command_data["dm_permission"]
        contexts = self.command_data["contexts"]

        new_data["version"] = version
        new_data["id"] = id
        new_data["name"] = command_name
        new_data["type"] = command_type
        new_data["options"] = formatted_options
        new_data["application_command"] = {"id": id, "application_id": self.application_id, "version": version,
                                           "default_member_permissions": default_member_permissions, "type": command_type,
                                           "nsfw": nsfw, "name": command_name, "description": command_description,
                                           "dm_permissions": dm_permissions, "contexts": contexts, "options": options,
                                           "attachments": [], "nonce": nonce}

        return new_data

    async def use_slash_command(self, user: UserClient, guild_id: int, channel_id: int,
                                                        inputs: Optional[dict[str, Any]] = None):

        url: str = "interactions"
        nonce: str = str((int(time()) * 1000 - 1420070400000) * 4194304)

        data = await self.reformat_data(data=self.command_data, nonce=nonce, inputs=inputs)

        session_id: str = "".join(choice(ascii_letters + digits) for _ in range(32))

        payload = {
            "type": 2,
            "application_id": self.application_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "data": data,
            "nonce": nonce,
            "session_id": session_id
        }

        header = AUTH_HEADER(authorization=user.token)
        response: ClientResponse = await self.client.request(
            url=url,
            method="POST",
            data=payload,
            headers=header  # pyright: ignore
        )

