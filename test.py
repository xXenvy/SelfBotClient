from SelfBotClient import Client


tokens = ["MTExNTcxNjg2Mzk2ODY3Mzg1NA.GQHXcU.aD5JN0BKr8Ohky6YDW0IAwzoBvJjvPTvUv3jQs"]


client = Client(api_version=10)
client.login(token=tokens)


async def execute():
    headers = {
        "authorization": tokens[0]
    }
    data = {
        "content": "Selfbot elo"
    }

    for _ in range(10):
        response = await client.request(url="channels/1115717164482187304/messages", method="POST", headers=headers, data=data)
        data = await response.json()


client.loop.run_until_complete(execute())