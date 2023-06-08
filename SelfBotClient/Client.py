from .HTTP import HTTPClient
from .typings import API_VERSION, ClientResponse, RGB_COLOR
from .enums import ChannelType
from .PermissionBuilder import PermissionBuilder
from collections.abc import AsyncIterable

from typing import Union

from asyncio import AbstractEventLoop
from time import sleep


class Client(HTTPClient):

    def __init__(
            self,
            api_version: API_VERSION,
            loop: AbstractEventLoop = None,
            logger: bool = True,
            request_latency: float = 0.1,
            ratelimit_additional_cooldown: float = 10
    ):

        super().__init__(api_version, loop, logger, request_latency, ratelimit_additional_cooldown)

    def login(self, token: Union[str, list[str]]) -> None:
        if self.logger._status:
            self.logger.info("Checking the provided tokens")

        self._tokens: Union[str, list[str]] = token
        self._check_tokens()
        sleep(1)

    async def send_message(self, channel_id: int, message_content: str) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The send_message function sends a message to the specified channel.

        :param self: Refer to the current instance of a class
        :param channel_id: int: Specify the channel to send the message to
        :param message_content: str: Specify the message that will be sent to each user
        :return: None if the message was sent successfully, or an asynciterable of clientresponse objects
        """

        for user in self.users:
            response: ClientResponse = await user.send_message(channel_id, message_content)
            yield response

    async def delete_channel(self, channel_id: int) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The delete_channel function deletes a channel from the server.

        :param self: Represent the instance of the class
        :param channel_id: int: Specify the channel to be deleted
        :return: An asynciterable of clientresponses
        """

        for user in self.users:
            response: ClientResponse = await user.delete_channel(channel_id)
            yield response

    async def create_channel(self, guild_id: int, name: str, channel_type: ChannelType,
                             topic: str = None, user_limit: int = None, position: int = None, nsfw: bool = False) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The create_channel function creates a channel in the specified guild.

        :param self: Refer to the object itself
        :param guild_id: int: Specify the guild id of the server you want to create a channel in
        :param name: str: Specify the name of the channel
        :param channel_type: ChannelType: Specify what type of channel you want to create
        :param topic: str: Set the topic of the channel
        :param user_limit: int: Set the maximum number of users allowed in a voice channel
        :param position: int: Set the position of the channel in the list
        :param nsfw: bool: Determine whether the channel is nsfw or not
        :return: An asynciterable, which is an iterable that can be used in a for loop
        """

        for user in self.users:
            response: ClientResponse = await user.create_channel(guild_id, name, channel_type, topic, user_limit, position, nsfw)
            yield response

    async def get_channels(self, guild_id: int) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The get_channels function is a coroutine that takes in a guild_id and returns an AsyncIterable of ClientResponse objects.
        The function iterates through the users list, calling get_channels on each user object with the given guild_id as its argument.
        It then yields each response to be used by other functions.

        :param self: Refer to the current instance of a class
        :param guild_id: int: Specify the guild id of the channels you want to get
        :return: An asynciterable of clientresponse objects
        """

        for user in self.users:
            response: ClientResponse = await user.get_channels(guild_id)
            yield response

    async def create_role(self,
                                guild_id: int,
                                name: str,
                                color: RGB_COLOR = None,
                                hoist: bool = False,
                                permissions: PermissionBuilder = None) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The create_role function creates a role in the specified guild.

        :param self: Access the attributes and methods of the class
        :param guild_id: int: Specify the guild in which you want to create a role
        :param name: str: Set the name of the role
        :param color: RGB_COLOR: Set the color of the role
        :param hoist: bool: Determine whether the role should be displayed separately in the user list
        :param permissions: PermissionBuilder: Set the permissions for the role
        :return: An asynciterable of clientresponse objects
        """

        for user in self.users:
            response: ClientResponse = await user.create_role(guild_id, name, color, hoist, permissions)
            yield response

    async def get_roles(self, guild_id: int) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The get_roles function is a coroutine that takes in a guild_id and returns an AsyncIterable of ClientResponse objects.
        The function iterates through the users attribute, which is an array of User objects, and calls the get_roles function on each user object.
        The get_roles function returns a ClientResponse object for each user.

        :param self: Refer to the current instance of the class
        :param guild_id: int: Specify the guild id of the server you want to get roles from
        :return: An asynciterable of clientresponse objects
        """
        for user in self.users:
            response: ClientResponse = await user.get_roles(guild_id)
            yield response

    async def delete_role(self, guild_id: int, role_id: int) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The delete_role function deletes a role from the guild.

        :param self: Refer to the current object
        :param guild_id: int: Specify the guild that you want to delete a role from
        :param role_id: int: Specify the role to be deleted
        :return: An asynciterable of clientresponse objects
        """

        for user in self.users:
            response: ClientResponse = await user.delete_role(guild_id, role_id)
            yield response

    async def ban_member(self, guild_id: int, user_id: int) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The ban_member function is used to ban a member from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that you want to ban a user from
        :param user_id: int: Specify the user that is to be banned
        :return: An asynciterable of clientresponse objects
        """

        for user in self.users:
            response: ClientResponse = await user.ban_member(guild_id, user_id)
            yield response

    async def kick_member(self, guild_id: int, user_id: int) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The kick_member function kicks a member from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that you want to kick a user from
        :param user_id: int: Identify the user to be kicked
        :return: An asynciterable of clientresponse objects
        """
        for user in self.users:
            resource: ClientResponse = await user.kick_member(guild_id, user_id)
            yield resource
