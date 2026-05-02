import re
from pathlib import Path
from urllib.parse import quote

import streamlit as st
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver

MODEL_NAME = "gemma4:e4b"
OBSIDIAN_DIR = Path("/Users/nariman/Documents/nariman")
WIKI_DIR = OBSIDIAN_DIR / "AI Wiki"
INDEX_FILE = WIKI_DIR / "index.md"
VAULT_NAME = OBSIDIAN_DIR.name

AGENT_PROMPT = """
You answer questions from a local Obsidian wiki.

Workflow:
- Start by reading `index.md` with `read_index`.
- Use `list_pages` to discover candidate wiki pages when needed.
- Use `read_page` to read the most relevant pages before answering.
- Base the answer only on the wiki files you read.

Rules:
- Cite claims inline with clickable markdown links returned by the tools, for example
  `[learning](obsidian://open?... )`.
- If the wiki does not contain enough information, say so plainly.
- Keep answers concise and grounded in the wiki.
- Do not invent page paths. Use the tools.
"""

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def build_wiki_path(path: Path) -> str:
    return str(path.relative_to(WIKI_DIR).with_suffix("")).replace("\\", "/")


def build_wiki_link(wiki_path: str) -> str:
    return f"[[{wiki_path}]]"


def build_obsidian_uri(file_path: Path) -> str:
    vault_name = quote(VAULT_NAME)
    vault_relative_path = quote(str(file_path.relative_to(OBSIDIAN_DIR)).replace("\\", "/"))
    return f"obsidian://open?vault={vault_name}&file={vault_relative_path}"


def build_markdown_link(label: str, file_path: Path) -> str:
    return f"[{label}]({build_obsidian_uri(file_path)})"


def get_page_path(wiki_path: str) -> Path:
    return WIKI_DIR / f"{wiki_path}.md"


def get_wiki_paths() -> list[str]:
    return sorted(
        build_wiki_path(path)
        for path in WIKI_DIR.rglob("*.md")
        if path != INDEX_FILE
    )


@tool
def read_index() -> str:
    """Read the wiki index. Use this first for every question."""
    return "\n".join(
        [
            f"Citation: {build_markdown_link('index', INDEX_FILE)}",
            read_text(INDEX_FILE)
        ]
    )



@tool
def list_pages() -> str:
    """List available wiki page paths excluding index."""
    return "\n".join(get_wiki_paths())


@tool
def read_page(wiki_path: str) -> str:
    """Read a wiki page by path like `topics/learning` or `sources/example`."""
    page_path = get_page_path(wiki_path)
    return "\n".join(
        [
            f"Page: {build_wiki_link(wiki_path)}",
            f"Citation: {build_markdown_link(wiki_path, page_path)}",
            read_text(page_path)
        ]
    )


model = ChatOllama(model=MODEL_NAME, temperature=0)
wiki_agent = create_agent(
    model=model,
    tools=[read_index, list_pages, read_page],
    system_prompt=AGENT_PROMPT,
    checkpointer=MemorySaver()
)

st.title("LLM Wiki Agent")
st.caption("Query your Obsidian knowledge base.")

if "messages" in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for message in st.session_state["messages"]:
    st.chat_message(message["role"]).write(message["content"])

question = st.chat_input("Ask a question about your wiki")

if question:
    st.session_state["messages"].append({"role": "user", "content": question})
    st.chat_message("user").write(question)

    result = wiki_agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question
                }
            ]
        },
        config={"configurable": {"thread_id": "1"}}
    )

    answer = result["messages"][-1].content
    st.session_state["messages"].append({"role": "assistant", "content": answer})
    st.chat_message("assistant").write(answer)