from SelfBotClient import Client, Permissions, PermissionBuilder, RGB_COLOR

tokens = ["TOKEN_1", "TOKEN_2"]

client = Client(api_version=10)
client.login(token=tokens)


async def create_role():
    role_permissions = PermissionBuilder(
        Permissions.MANAGE_ROLES,
        Permissions.MUTE_MEMBERS,
        Permissions.KICK_MEMBERS
    )  # We enter after the comma which permissions we want to have.

    async for role_response in client.create_role(
                                guild_id=123,
                                name="example role",
                                color=RGB_COLOR(R=66, G=135, B=245),
                                permissions=role_permissions):

        role_data: dict = await role_response.json()
        role_id: int = role_data.get("id")

        await client.delete_role(guild_id=123, role_id=role_id)  # just for example


async def main():
    await create_role()


if __name__ == "__main__":
    client.run_async(main())
