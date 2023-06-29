from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any
from .errors import GatewayNotConnected
from ..typings import AUTH_HEADER

from time import time
from random import choice, sample
from string import ascii_letters, digits

from requests_toolbelt import MultipartEncoder
from json import dumps
from asyncio import sleep

if TYPE_CHECKING:
    from ..user import UserClient
    from ..client import Client, ClientResponse
    from ..gateway.gateway import GatewayConnection


class Application:

    def __init__(self, client: Client, application_id: int):
        self.client: Client = client
        self.application_id: int = application_id
        self._commands: Optional[dict] = None

    def __repr__(self):
        return f"<DiscordApplication(id={self.application_id})>"

    async def search_slash_command(self, user: UserClient, guild_id: int, query: str, limit: int = 3) -> Optional[list[SlashCommand]]:
        gateway: Optional[GatewayConnection] = user.gateway_connection
        if not gateway:
            raise GatewayNotConnected(user)

        op: int = 24  # Code for requesting slash commands
        nonce: str = str((int(time()) * 1000 - 1420070400000) * 4194304)

        data = {
            "op": op,
            "d": {"guild_id": guild_id,
                  "nonce": nonce,
                  "type": 1,
                  "application_id": self.application_id,
                  "query": query,
                  "limit": limit},
        }

        await gateway.application_update_request(data, self.await_for_application_commands_update)
        data: Optional[dict] = None

        for retry in range(5):  # awaiting to gateway change self._commands to commands data
            await sleep(1)
            if self._commands:
                data = self._commands
                self._commands = None
                break

        if not data:
            return None

        application_commands: list[dict] = data["application_commands"]
        slash_commands: Optional[list[SlashCommand]] = []

        for command_data in application_commands:
            if int(command_data["application_id"]) == self.application_id:
                slash_commands.append(SlashCommand(command_data, self.client))

        return slash_commands

    async def await_for_application_commands_update(self, data: dict):
        self._commands = data


class SlashCommand:

    def __init__(self, command_data: dict, client: Client):
        self.client: Client = client
        self.command_data: dict = command_data
        self.command_name: str = self.command_data["name"]
        self.application_id: int = self.command_data["application_id"]

    def __repr__(self):
        return f"<SlashCommand(name={self.command_name}, application_id={self.application_id})>"

    async def reformat_data(self, data: dict, nonce: str, inputs: Optional[dict[str, Any]] = None):
        new_data: dict = {}
        formatted_options: list[Optional[dict]] = []

        version: str = data["version"]
        id: str = data["id"]
        command_name: str = data["name"]
        type: int = data["type"]
        options: list[dict] = []

        if inputs:
            options = data["options"]
            for option in options:
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

        default_member_permissions = self.command_data["default_member_permissions"]
        nsfw: bool = self.command_data["nsfw"]
        command_description: str = self.command_data["description"]
        dm_permissions: bool = self.command_data["dm_permission"]
        contexts = self.command_data["contexts"]

        new_data["version"] = version
        new_data["id"] = id
        new_data["name"] = command_name
        new_data["type"] = type
        new_data["options"] = formatted_options
        new_data["application_command"] = {"id": id, "application_id": self.application_id, "version": version,
                                           "default_member_permissions": default_member_permissions, "type": type,
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

