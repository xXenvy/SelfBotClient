**Project only for educational purposes! 🤓**

[![Downloads](https://static.pepy.tech/personalized-badge/selfbotclient?period=total&units=international_system&left_color=grey&right_color=brightgreen&left_text=Downloads)](https://pepy.tech/project/selfbotclient)
[![Documentation Status](https://readthedocs.org/projects/selfbotclient/badge/?version=latest)](https://selfbotclient.readthedocs.io/en/latest/?badge=latest)
![master](https://img.shields.io/github/last-commit/badges/shields/master)
![commits](https://badgen.net/github/commits/xXenvy/selfbotclient/master)

## 🌐 Docs
https://selfbotclient.readthedocs.io/en/latest/

# ⚡ Fast Self Bot Client
- Token Checker | `1` token / `140`ms
- +10 requests / 1s `(using tasks)`

https://github.com/xXenvy/SelfBotClient/assets/111158232/ede9fb47-d489-4d9a-b58d-95c06dea6fe9


# 🔧 Full control
- A separate method to send your own requests
- Ability to manage individual selfbots

# 📌 Ratelimit handler
- The library itself detects whether you have reached the ratelimit of the discord and, if so, forces you to wait a certain time.
![Test](https://i.imgur.com/hTUFQKF.png)
# 🛠️ Installation
```shell
pip install -U selfbotclient
```
# 💫 Usage
```py
from SelfBotClient import Client

tokens: list[str] = ["TOKEN_1", "TOKEN_2"]

client: Client = Client(api_version=10)
client.login(token=tokens)
```
**See more examples on github:** [Examples](https://github.com/xXenvy/SelfBotClient/tree/master/examples)
