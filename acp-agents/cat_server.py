from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent

server = Server()
model = ChatOllama(model="llama3.2")
cat = create_react_agent(
    model=model,
    tools=[],
    prompt="You are a cat, answer every question with 'meow', do not use any other words."
)

@server.agent()
async def cat_agent(messages: list[Message])-> AsyncGenerator[RunYield, RunYieldResume]:
    query = " ".join(
        part.content
        for m in messages
        for part in m.parts
    )

    response = cat.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": query
                }
            ]
        }
    )

    yield Message(parts=[MessagePart(content=response["messages"][-1].content)])

server.run(port=8001)














