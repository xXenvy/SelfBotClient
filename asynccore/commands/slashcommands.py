from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Any
from time import time
from random import choice
from string import ascii_letters, digits

from ..typings import AUTH_HEADER

if TYPE_CHECKING:
    from ..user import UserClient
    from ..client import Client, ClientResponse


class SlashCommand:
    """
    A class representing the SlashCommand of the Application.

    :param command_data: Store the command data
    :param client: Get the client object
    """

    def __init__(self, command_data: dict, client: Client):

        self.client: Client = client
        self.command_data: dict = command_data
        self.application_id: int = self.command_data["application_id"]
        self.command_name: str = self.command_data["name"]

        self.sub_command: Optional[str] = self.command_data.get("sub_command")
        self.global_name: str = self.command_data["global_name"]

    def __repr__(self):
        return f"<SlashCommand(name={self.global_name}, application_id={self.application_id})>"

    def _format_slash_command(self, option: dict, inputs: dict, options: list) -> list:
        """
        A function that formats the slashcommand data that must be given in the request

        :param option: Pass the option data to the function
        :param inputs: Store the input data for the command
        :param options: Store the data from each option
        """

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
                        options.append(__option_data)
        return options

    def _format_sub_command(self, command_type: int, option: dict, inputs: dict, options: list) -> list:
        """
        A function that formats the subcommand data that must be given in the request

        :param command_type: Determine what type of command is being used
        :param option: Pass the option data to the function
        :param inputs: Store the input data for the command
        :param options: Store the data from each option
        """

        option_inputs_list: list[Optional[dict]] = []

        if len(option["options"]) >= 1:
            for subcommand_option in option["options"]:
                for key, value in subcommand_option.items():
                    if key == "name":
                        for input_name, input_value in inputs.items():
                            if value == input_name:
                                _type: int = subcommand_option["type"]
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
        options.append(option_data)

        return options

    async def _reformat_data(self, data: dict, nonce: str, inputs: Optional[dict[Any, Any]] = None) -> dict:
        """
        The reformat_data function is used to reformat the data that is sent to Discord's API.
        The function takes in a dictionary of data, a nonce string, and an optional inputs dictionary.

        :param data: command_data from __init__ method
        :param nonce: Generate a random string that is used to identify the command
        :param inputs: Pass in the inputs for the command

        ngl this method must be rewrited.
        """

        new_data: dict = {}
        formatted_options: list[Optional[dict]] = []
        if not inputs:
            inputs = {}

        version: str = data["version"]
        command_id: str = data["id"]
        command_name: str = data["name"]

        command_type: int = data["type"]
        options: Optional[list[dict]] = data.get("options")

        if options:
            for option in options:
                if option["type"] == 3:  # Normal command
                    for data in self._format_slash_command(option, inputs, []):
                        formatted_options.append(data)

                elif option["type"] == 1:  # Command with subcommands
                    for data in self._format_sub_command(command_type, option, inputs, []):
                        formatted_options.append(data)

        default_member_permissions = self.command_data["default_member_permissions"]
        nsfw: bool = self.command_data["nsfw"]
        command_description: str = self.command_data["description"]
        dm_permissions: bool = self.command_data["dm_permission"]
        contexts = self.command_data["contexts"]

        new_data["version"] = version
        new_data["id"] = command_id
        new_data["name"] = command_name
        new_data["type"] = command_type
        new_data["options"] = formatted_options
        new_data["application_command"] = {"id": command_id, "application_id": self.application_id,
                                           "version": version, "default_member_permissions": default_member_permissions,
                                           "type": command_type, "nsfw": nsfw, "name": command_name,
                                           "description": command_description, "dm_permissions": dm_permissions,
                                           "contexts": contexts, "options": options, "attachments": [], "nonce": nonce}

        return new_data

    async def use_slash_command(self, user: UserClient, guild_id: int, channel_id: int,
                                                        inputs: Optional[dict[str, Any]] = None) \
            -> Optional[ClientResponse]:
        """
        The use_slash_command function is used to send a slash command to Discord.

        :param user: Send the request to discord
        :param guild_id: Specify the guild id of the server you want to use this command in
        :param channel_id: Specify the channel id of the channel where you want to send your command
        :param inputs: Pass in the inputs that is needed for the command to run
        """

        url: str = "interactions"
        nonce: str = str((int(time()) * 1000 - 1420070400000) * 4194304)

        data = await self._reformat_data(data=self.command_data, nonce=nonce, inputs=inputs)

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
        return response
