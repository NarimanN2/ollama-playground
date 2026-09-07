from typing import Literal, TypedDict

import streamlit as st
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_tavily import TavilySearch
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel


class ResearchState(TypedDict, total=False):
    query: str
    sources: list[dict[str, str]]
    answer: str
    validation_decision: str
    validation_feedback: str
    draft_attempts: int


class ValidationResult(BaseModel):
    decision: Literal["pass", "reject"]
    feedback: str


writer_model = ChatOllama(model="gemma4:e2b", temperature=0)
validator_model = ChatOllama(model="gemma4:e2b", temperature=0).with_structured_output(
    ValidationResult
)
tavily_search = TavilySearch(max_results=3)

DRAFT_PROMPT = """Answer the question using only the sources below. Put a numbered
citation such as [1] after every factual sentence. At the end, add a References:
section with each cited source on its own line in this form: [1] URL. If validator
feedback is provided, correct it.

Question: {query}

Validator feedback:
{feedback}

Sources:
{sources}"""

VALIDATOR_PROMPT = """Check the answer against the question and sources.

Return pass when the answer directly answers the question and its factual claims
are supported by the cited sources. Otherwise return reject with short, actionable
feedback for rewriting the answer using the same sources.

Question: {query}

Answer:
{answer}

Sources:
{sources}"""

def format_sources_for_prompt(sources: list[dict[str, str]]) -> str:
    return "\n\n".join(
        f"[{index}] URL: {source['url']}\nContent: {source['content']}"
        for index, source in enumerate(sources, start=1)
    )


def search(state: ResearchState) -> dict:
    response = tavily_search.invoke({"query": state["query"]})
    sources = [
        {"url": item["url"], "content": item["content"]}
        for item in response["results"]
    ]

    return {"sources": sources}


def draft(state: ResearchState) -> dict:
    chain = ChatPromptTemplate.from_template(DRAFT_PROMPT) | writer_model
    response = chain.invoke(
        {
            "query": state["query"],
            "feedback": state.get("validation_feedback", ""),
            "sources": format_sources_for_prompt(state["sources"]),
        }
    )

    return {
        "answer": response.content,
        "draft_attempts": state.get("draft_attempts", 0) + 1
    }


def validate(state: ResearchState) -> dict:
    chain = ChatPromptTemplate.from_template(VALIDATOR_PROMPT) | validator_model
    response = chain.invoke(
        {
            "query": state["query"],
            "answer": state["answer"],
            "sources": format_sources_for_prompt(state["sources"]),
        }
    )

    return {
        "validation_decision": response.decision,
        "validation_feedback": response.feedback
    }


def next_step(state: ResearchState) -> str:
    if state["validation_decision"] == "pass":
        return "end"
    if (
        state["validation_decision"] == "reject"
        and state.get("draft_attempts", 0) < 2
    ):
        return "draft"
    return "end"


builder = StateGraph(ResearchState)
builder.add_node("search", search)
builder.add_node("draft", draft)
builder.add_node("validate", validate)
builder.add_edge(START, "search")
builder.add_edge("search", "draft")
builder.add_edge("draft", "validate")
builder.add_conditional_edges(
    "validate", next_step, {"draft": "draft", "end": END}
)
graph = builder.compile()


st.title("AI Researcher")
query = st.text_input("Enter your research query:")

if query:
    with st.spinner("Researching..."):
        result = graph.invoke({"query": query})

    st.markdown(result["answer"])
    if result["validation_decision"] == "pass":
        st.success("Verified")
    else:
        st.warning(f"Verification ended: {result['validation_decision']}")
        st.write(result["validation_feedback"])
