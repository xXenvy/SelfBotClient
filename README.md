
# ⚡ Fast Self Bot Client
- Token Checker | `1` token / `140`ms
- 3 requests / 1s `(in feature 10 requests / 1s using threads)`

# 🔧 Full control
- A separate method to send your own requests
- Ability to manage individual selfbots

# 📌 Ratelimit handler

- The library itself detects whether you have reached the ratelimit of the discord and, if so, forces you to wait a certain time.
# 🛠️ Installation
```shell
pip install -U selfbotclient
```
# 💫 Examples
```py
from SelfBotClient import Client

tokens: list[str] = ["TOKEN_1", "TOKEN_2"]

client: Client = Client(api_version=10)
client.login(token=tokens)
```
**See more examples on github:** [Examples](https://github.com/xXenvy/SelfBotClient/tree/master/examples)
