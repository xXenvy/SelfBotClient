from asynccore import Client, UserClient


""" Normal events handlers """
client: Client = Client(api_version=10)
client.login(tokens=["TOKEN_1", "TOKEN_2"])


@client.gateway.event(event_name="on_ready")
async def ready(user: UserClient):
    print(f"Account: {user.name} is ready.")


@client.gateway.event(event_name="on_message_create")
async def on_message(user: UserClient, message_data: dict):
    print(message_data)

client.gateway.run()


""" OOP events handlers """


class client(Client):

    def __init__(self):
        super().__init__(api_version=10)
        self.login(tokens=["TOKEN_1", "TOKEN_2"])

    async def on_ready(self, user: UserClient) -> None:
        print(f"Account: {user.name} is ready.")

    async def on_message_create(self, user: UserClient, message_data: dict) -> None:
        print(message_data)


client = client()
client.gateway.run()
