Using SlashCommands
===============
.. code-block:: python
  :linenos:

  from asynccore import Client, UserClient
  from asynccore.commands import Application, SlashCommand

  from typing import Optional


  client: Client = Client(api_version=10)
  client.login(tokens=["TOKEN_1", "TOKEN_2"])


  async def main():
      app: Application = Application(client=client, application_id=bot_id)
      " Bot Application Object "

      user: UserClient = client.users[0]
      " user to search and use slash command "

      commands: list[Optional[SlashCommand]] = await app.search_slash_command(
          query="ban",
          user=user,
          guild_id=983442350963576863,
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

      await main()


  client.gateway.run()

