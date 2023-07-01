from __future__ import annotations

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client
    from ..user import UserClient
    from ..gateway.gateway import GatewayConnection

from .SlashCommands import SlashCommand
from .errors import GatewayNotConnected
from time import time
from asyncio import sleep


class Application:

    def __init__(self, client: Client, application_id: int):
        self.client: Client = client
        self.application_id: int = application_id
        self._commands: Optional[dict] = None

        self._cached_commands: list[Optional[SlashCommand]] = []

    def __repr__(self):
        return f"<DiscordApplication(id={self.application_id})>"

    def get_slash_command_from_cache(self, command_name: str) -> Optional[SlashCommand]:
        for slash in self._cached_commands:
            if slash.global_name == command_name:
                return slash

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

        await gateway.application_update_request(data, self._await_for_application_commands_update)
        data: Optional[dict] = None

        for retry in range(5):  # awaiting to gateway change self._commands to commands data
            await sleep(1)
            if self._commands:
                data = self._commands
                self._commands = None
                break

        if not data:
            return []

        application_commands: list[dict] = data["application_commands"]
        slash_commands: Optional[list[SlashCommand]] = []

        for command_data in application_commands:
            if int(command_data["application_id"]) == self.application_id:

                if isinstance(command_data.get("options"), list):  # Command with subcommand

                    for sub_command_data in command_data.get("options"):

                        sub_command_data["application_id"] = command_data["application_id"]
                        sub_command_data["version"] = command_data["version"]
                        sub_command_data["id"] = command_data["id"]
                        sub_command_data["default_member_permissions"] = command_data["default_member_permissions"]
                        sub_command_data["nsfw"] = command_data["nsfw"]
                        sub_command_data["dm_permission"] = command_data["dm_permission"]
                        sub_command_data["contexts"] = command_data["contexts"]
                        sub_command_data["global_name"] = f"{command_data['name']} {sub_command_data['name']}"
                        sub_command_data["sub_command"] = sub_command_data["name"]
                        sub_command_data["name"] = command_data["name"]

                        options: dict = {
                            "type": sub_command_data["type"],
                            "name": sub_command_data["sub_command"],
                        }

                        if sub_command_data.get("options"):
                            options["options"] = sub_command_data.get("options")
                        else:
                            options["options"] = []

                        sub_command_data["options"] = [options]

                        sub_command = SlashCommand(command_data=sub_command_data, client=self.client)
                        slash_commands.append(sub_command)

                else:
                    command_data["global_name"] = command_data["name"]
                    slash_commands.append(SlashCommand(command_data=command_data, client=self.client))

        for slash in slash_commands:
            if slash not in self._cached_commands:
                self._cached_commands.append(slash)

        return slash_commands

    async def _await_for_application_commands_update(self, data: dict):
        self._commands = data