import asyncio
import os

from fastmcp import Client
from fastmcp.client.auth import OAuth
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama


MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000/mcp")
CLIENT_NAME = os.getenv("CLIENT_NAME", "Stocks Agent")
OLLAMA_MODEL = ChatOllama(model="llama3.2")
USER_QUERY = "Analyze how revenue of MSFT is changing over time."


async def main() -> None:
    oauth = OAuth(mcp_url=MCP_SERVER_URL, client_name=CLIENT_NAME)

    async with Client(MCP_SERVER_URL, auth=oauth) as mcp_client:
        tools = await load_mcp_tools(mcp_client.session)
        agent = create_agent(OLLAMA_MODEL, tools)
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": USER_QUERY}]}
        )
        print(response["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
