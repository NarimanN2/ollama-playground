import asyncio

from acp_sdk.client import Client


async def main():
    async with Client(base_url="http://localhost:8001") as cat_client, Client(base_url="http://localhost:8002") as dog_client:
        cat_result = await cat_client.run_sync(agent='cat_agent', input="Hello, how are you?")
        print(cat_result.output[0].parts[0].content)

        dog_result = await dog_client.run_sync(agent='dog_agent', input=cat_result.output[0].parts[0].content)
        print(dog_result.output[0].parts[0].content)

asyncio.run(main())



