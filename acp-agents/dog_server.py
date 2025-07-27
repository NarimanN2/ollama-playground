from collections.abc import AsyncGenerator

from acp_sdk.models import Message, MessagePart
from acp_sdk.server import RunYield, RunYieldResume, Server
from crewai import Agent, LLM, Task, Crew

server = Server()
model = LLM(model="ollama/llama3.2")
dog = Agent(
    role='Dog',
    goal="Answer every question with 'woof'",
    backstory="Do not use any other words.",
    llm=model
)

@server.agent()
async def dog_agent(messages: list[Message])-> AsyncGenerator[RunYield, RunYieldResume]:
    query = " ".join(
        part.content
        for m in messages
        for part in m.parts
    )

    task = Task(
        description=query,
        expected_output="A response to user's query",
        agent=dog
    )
    crew = Crew(agents=[dog], tasks=[task])
    crew.kickoff()

    yield Message(parts=[MessagePart(content=task.output.raw)])

server.run(port=8002)














