from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from .errors import GatewayNotConnected

from time import time
from random import choice
from string import ascii_letters, digits
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
                break

        if not data:
            return None

        application_commands: list[dict] = data["application_commands"]
        slash_commands: Optional[list[SlashCommand]] = []

        for command_data in application_commands:
            slash_commands.append(SlashCommand(command_data))

        return slash_commands

    async def await_for_application_commands_update(self, data: dict):
        self._commands = data


class SlashCommand:

    def __init__(self, command_data: dict):
        self.command_data: dict = command_data
        self.command_name: str = self.command_data["name"]
        self.application_id: int = self.command_data["application_id"]

    def __repr__(self):
        return f"<SlashCommand(name={self.command_name}, application_id={self.application_id})>"

    async def use_slash_command(self, guild_id: int, channel_id: int):
        url: str = "interactions"

        nonce: str = str((int(time()) * 1000 - 1420070400000) * 4194304)
        session_id: str = "".join(choice(ascii_letters + digits) for _ in range(32))

        # body
        payload = {
            "type": 2,
            "application_id": self.application_id,
            "guild_id": guild_id,
            "channel_id": channel_id,
            "data": self.command_data,
            "nonce": nonce,
            "session_id": session_id
        }

