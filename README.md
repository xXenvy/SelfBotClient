### The most powerful selfbotting library.
> ⚠️ Project only for educational purposes! 🤓

[![Downloads](https://static.pepy.tech/personalized-badge/selfbotclient?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/selfbotclient)
[![Documentation Status](https://readthedocs.org/projects/selfbotclient/badge/?version=latest)](https://selfbotclient.readthedocs.io/en/latest/?badge=latest)
![master](https://img.shields.io/github/last-commit/badges/shields/master)
![commits](https://badgen.net/github/commits/xXenvy/selfbotclient/master)

# 🔧 AsyncCore Features
- Modern Pythonic API using `async` and `await`
- Proper rate limit handling
- Optimised in both speed and memory
- Properly typehinted

## ⚡ High Speed
https://github.com/xXenvy/SelfBotClient/assets/111158232/ede9fb47-d489-4d9a-b58d-95c06dea6fe9

## 🔧 Full control
- A separate method to send your own requests
- Ability to manage individual selfbots
- Simple multi-account management

## 📌 Ratelimit handler
- The library itself detects whether you have reached the ratelimit of the discord and, if so, forces you to wait a certain time.
![Test](https://i.imgur.com/hTUFQKF.png)

# 🛠️ Installation
```shell
pip install -U asynccore
```
# 💫 Example
**See more examples on github:** [JUMP!](https://github.com/xXenvy/SelfBotClient/tree/master/examples)
```py
from asynccore import Client, UserClient

client: Client = Client(api_version=10)
client.login(tokens=["TOKEN_1", "TOKEN_2"])


async def send_example_message(user: UserClient, channel_id: int) -> None:
    await user.send_message(channel_id=channel_id, message_content="Hi")


@client.gateway.event(event_name="on_ready")
async def ready(user: UserClient):
    print(f"Account: {user.name} is ready.")
    await send_example_message(user=user, channel_id=123)

client.gateway.run(reconnect=True)
```

# 🧷 Links
- [Documentation](https://asynccore.readthedocs.io/en/latest/index.html)
- [Report a bug or feature](https://github.com/xXenvy/AsyncCore/issues/new/choose)
