Basic Spam
===============
.. code-block:: python
  :linenos:

  from asynccore import Client

  tokens = ["TOKEN_1", "TOKEN_2"]

  client = Client(api_version=10)
  client.login(tokens=tokens)


  async def spam_messages(channel_id: int, message_content: str, times: int) -> None:

      for _ in range(times):
          async for response in client.send_message(channel_id=channel_id,
                                                    message_content=message_content):
              message_data: dict = await response.json()
              message_id: int = message_data.get("id")
              # do something


  async def main():
      await spam_messages(channel_id=123, message_content="hi!", times=100)


  if __name__ == "__main__":
      "I recommend that you run async methods this way."
      "I'm not sure how asyncio.run(func), for example, will behave."

      client.run_async(main())

