from .http import HTTPClient
from .typings import API_VERSION, ClientResponse, RGB_COLOR
from .enums import ChannelType
from .permissionbuilder import PermissionBuilder
from .threads import Threads

from collections.abc import AsyncIterable

from typing import Union
from asyncio import AbstractEventLoop


class Client(HTTPClient):
    __version__: str = "1.0.2"

    def __init__(
            self,
            api_version: API_VERSION,
            loop: AbstractEventLoop = None,
            logger: bool = True,
            request_latency: float = 0.1,
            ratelimit_additional_cooldown: float = 10,
            use_threading: bool = False
    ):
        """
        The __init__ function is called when the class is instantiated.
        It sets up all of the attributes that are needed for the class to function properly.


        :param self: Represent the instance of the class
        :param api_version: API_VERSION: Set the api version of the client
        :param loop: AbstractEventLoop: Specify the event loop that the client will use
        :param logger: bool: Enable/disable logging
        :param request_latency: float: Set the time between requests
        :param ratelimit_additional_cooldown: float: Add a cooldown to the ratelimit
        :param use_threading: bool: Determine if the client should use threading
        :return: None
        """

        super().__init__(api_version, loop, logger, request_latency, ratelimit_additional_cooldown)

        if use_threading:
            self.thread: Threads = Threads(client=self)

    def login(self, token: Union[str, list[str]]) -> None:
        """
        The login function is used to check the provided tokens.

        :param self: Represent the instance of the class
        :param token: Union[str, list[str]] tokens to check
        :return: None
        """

        if self.logger._status:
            self.logger.info("Checking the provided tokens")

        self._tokens: Union[str, list[str]] = token
        self._check_tokens()

    async def send_message(self, channel_id: int, message_content: str) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The send_message function sends a message to the specified channel.

        :param self: Refer to the current instance of a class
        :param channel_id: int: Specify the channel to send the message to
        :param message_content: str: Specify the message that will be sent to each user
        :return: An asynciterable of clientresponse objects or None
        """

        for user in self.users:
            response: ClientResponse = await user.send_message(channel_id, message_content)
            yield response

    async def delete_channel(self, channel_id: int) -> Union[None, ClientResponse]:
        """
        The delete_channel function deletes a channel from the server.

        :param self: Refer to the object itself
        :param channel_id: int: Specify the channel that is to be deleted
        :return: A clientresponse object or None
        """

        for user in self.users:
            response: ClientResponse = await user.delete_channel(channel_id)
            if response.status == 200:
                return response

    async def delete_channels(self, channel_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The delete_channels function takes a list of channel_ids and deletes them.
            It returns an AsyncIterable of ClientResponse objects, which can be used to check the status code for each request.

        :param self: Access the class variables and methods
        :param channel_ids: list[int]: Specify the list of channel ids that will be deleted
        :return: An asynciterable of clientresponse objects or None
        """

        while len(channel_ids):
            for user in self.users:
                channel_id: int = channel_ids.pop(0)
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
        :return: An asynciterable of clientresponse objects or None
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
        :return: An asynciterable of clientresponse objects or None
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
        :return: An asynciterable of clientresponse objects or None
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
        :return: An asynciterable of clientresponse objects or None
        """
        for user in self.users:
            response: ClientResponse = await user.get_roles(guild_id)
            yield response

    async def delete_roles(self, guild_id: int, role_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:

        """
        The delete_roles function is a coroutine that takes in two arguments:
            1. guild_id - the id of the server to delete roles from
            2. role_ids - a list of ids for each role to be deleted

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that the roles are being deleted from
        :param role_ids: list[int]: Specify the roles that are to be deleted
        :return: An asynciterable of clientresponse objects or None
        """

        while len(role_ids):
            for user in self.users:
                role_id: int = role_ids.pop(0)
                response: ClientResponse = await user.delete_role(guild_id, role_id)
                yield response

    async def delete_role(self, guild_id: int, role_id: int) -> Union[None, ClientResponse]:
        """
        The delete_role function deletes a role from the guild.

        :param self: Refer to the current object
        :param guild_id: int: Specify the guild that you want to delete a role from
        :param role_id: int: Specify the role to be deleted
        :return: clientresponse object or None
        """

        for user in self.users:
            response: ClientResponse = await user.delete_role(guild_id, role_id)
            if response.status == 204:
                return response

    async def get_bans(self, guild_id: int) -> Union[None, ClientResponse]:
        """
        The get_bans function returns a list of banned users in the guild.


        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild id of the server you want to get banned users from
        :return: A clientresponse object or None
        """

        for user in self.users:
            response: ClientResponse = await user.get_bans(guild_id)
            if response.status == 200:
                return response

    async def ban_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The ban_member function is used to ban a member from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that you want to ban a user from
        :param user_id: int: Specify the user that is to be banned
        :return: clientresponse object or None
        """

        for user in self.users:
            response: ClientResponse = await user.ban_member(guild_id, user_id)
            if response.status == 204:
                return response

    async def unban_members(self, guild_id: int, user_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The unban_members function is a coroutine that takes in a guild_id and user_ids list.
        It then iterates through the users list, popping off the first user id from the
        user_ids list and passing it to unban_member function of each client. If there is no
        response or if there was an error, it will return None. Otherwise, it will yield back
        the response.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild id of the server you want to unban members from
        :param user_ids: list[int]: Store the list of user ids to unban
        :return: A union of none or asynciterable[clientresponse]
        """

        while len(user_ids):
            for user in self.users:
                user_id: int = user_ids.pop(0)
                response: ClientResponse = await user.unban_member(guild_id, user_id)
                if response.status == 204:
                    yield response

    async def unban_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The unban_member function unban a user from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that you want to unban a member from
        :param user_id: int: Specify the user id of the member to unban
        :return: A clientresponse object or None
        """

        for user in self.users:
            response: ClientResponse = await user.unban_member(guild_id, user_id)
            if response.status == 204:
                return response

    async def ban_members(self, guild_id: int, user_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:

        """
        The ban_members function is a coroutine that takes in a guild_id and user_ids list.
        It then iterates through the users list, popping off the first user id from the
        user_ids list and passing it to ban_member function of each client. The response
        from each client is yielded back to whatever called this function.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild to ban the user from
        :param user_ids: list[int]: Store the list of user ids that will be banned
        :return: A union of none or an asynciterable[clientresponse]
        """

        while len(user_ids):
            for user in self.users:
                user_id: int = user_ids.pop(0)
                response: ClientResponse = await user.ban_member(guild_id, user_id)
                yield response

    async def kick_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The kick_member function kicks a member from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that you want to kick a user from
        :param user_id: int: Identify the user to be kicked
        :return: clientresponse object or None
        """
        for user in self.users:
            response: ClientResponse = await user.kick_member(guild_id, user_id)
            if response.status == 204:
                return response

    async def kick_members(self, guild_id: int, user_ids: list[int]) -> Union[None, AsyncIterable[ClientResponse]]:
        """
        The kick_member function kicks a member from the guild.

        :param self: Represent the instance of the class
        :param guild_id: int: Specify the guild that you want to kick a user from
        :param user_ids: list[int]: Identify the user to be kicked
        :return: A union of none or an asynciterable[clientresponse]
        """

        while len(user_ids):
            for user in self.users:
                user_id: int = user_ids.pop(0)
                response: ClientResponse = await user.kick_member(guild_id, user_id)
                yield response

    async def get_member(self, guild_id: int, user_id: int) -> Union[None, ClientResponse]:
        """
        The get_member function is used to get a member from the guild.
            Parameters:
                guild_id (int): The ID of the guild to get the member from.
                user_id (int): The ID of the user to get as a member.

        :param self: Access the class variables and methods
        :param guild_id: int: Specify the guild that you want to get a member from
        :param user_id: int: Specify the user id of the member you want to get
        :return: A clientresponse object or None
        """

        for user in self.users:
            response: ClientResponse = await user.get_member(guild_id, user_id)
            if response.status == 200:
                return response

    async def edit_member(self, guild_id: int, user_id: int,
                                                                nickname: str = None,
                                                                add_roles: list[int] = None,
                                                                remove_roles: list[int] = None) -> Union[None, ClientResponse]:

        """
        The edit_member function allows you to edit a member of a guild.

        :param self: Refer to the object itself
        :param guild_id: int: Specify the guild that you want to edit a member in
        :param user_id: int: Specify the user that you want to edit
        :param nickname: str: Change the nickname of a user in a guild
        :param add_roles: list[int]: Add roles to a user
        :param remove_roles: list[int]: Remove roles from a user
        :return: A clientresponse object or None
        """

        for user in self.users:
            response: ClientResponse = await user.edit_member(guild_id, user_id, nickname, add_roles, remove_roles)
            if response and response.status == 200:
                return response
