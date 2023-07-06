from __future__ import annotations

from typing import Optional, TYPE_CHECKING
from time import time
from asyncio import sleep

from .slashcommands import SlashCommand
from ..gateway.errors import GatewayNotConnected

if TYPE_CHECKING:
    from ..client import Client
    from ..user import UserClient
    from ..gateway.gateway import GatewayConnection


class Application:
    """
    A class representing the discord Application

    :param client: Pass the client object to the class
    :param application_id: Identify the application
    """

    def __init__(self, client: Client, application_id: int):

        self.client: Client = client
        self.application_id: int = application_id
        self._commands: Optional[dict] = None

        self._cached_commands: list[Optional[SlashCommand]] = []

    def __repr__(self):
        return f"<DiscordApplication(id={self.application_id})>"

    def get_slash_command_from_cache(self, command_name: str) -> Optional[SlashCommand]:
        """
        The get_slash_command_from_cache function is a helper function that returns the SlashCommand object
        from the cache if it exists.

        :param command_name: Specify the name of the command to be retrieved from cache
        """

        if len(self._cached_commands) >= 1:
            for slash in self._cached_commands:
                if slash.global_name == command_name:  # pyright: ignore
                    return slash

        return None

    async def search_slash_command(self, user: UserClient, guild_id: int, query: str, limit: int = 3) \
            -> Optional[list[SlashCommand]]:

        """
        The search_slash_command function searches for slash commands in a guild.

        :param user: Get the gateway connection of the user
        :param guild_id: Specify the guild id of the server you want to search for commands in
        :param query: Search for commands with the given name
        :param limit: Limit the number of results returned
        """

        gateway: Optional[GatewayConnection] = user.gateway_connection

        if not gateway:
            raise GatewayNotConnected(f"{user} does not have a gateway connection. ")

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

        for _ in range(5):  # awaiting to gateway change self._commands to commands data
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
                command_options: Optional[list[dict]] = command_data.get("options")

                if command_options and command_options[0].get("type") == 1:

                    for sub_command_data in command_data["options"]:

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
        """
        The _await_for_application_commands_update function is a coroutine that
        awaits for the application commands to be updated.

        :param data: Store the commands in a dictionary
        """
        self._commands: Optional[dict] = data
