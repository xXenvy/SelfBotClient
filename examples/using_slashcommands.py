from SelfBotClient import Client, UserClient

from SelfBotClient.commands import Application, SlashCommand
from typing import Optional


client: Client = Client(api_version=10, logger=False)
client.login(tokens=["TOKEN_1", "TOKEN_2"])


async def main():
    app: Application = Application(client=client, application_id=bot_id)
    " Bot Application Object "

    user: UserClient = client.users[0]
    " user to search and use slash command "

    commands: list[Optional[SlashCommand]] = await app.search_slash_command(
        query="ban",
        user=user,
        guild_id=guild_id,
        limit=1
    )
    for command in commands:
        await command.use_slash_command(
            user=user,
            channel_id=123,
            guild_id=123,
            inputs={"command_input_name": "command_input_value"}
        )


@client.gateway.event(event_name="on_ready")
async def ready(user: UserClient):
    print(f"Account: {user.name} is ready.")

    client.loop.create_task(main())


client.gateway.run()
