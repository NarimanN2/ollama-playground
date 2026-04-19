import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

MODEL_NAME = "gemma4:e4b"
OBSIDIAN_DIR = Path("PUT_YOUR_OBSIDIAN_PATH")
RAW_DIR = OBSIDIAN_DIR / "Clippings"
WIKI_DIR = OBSIDIAN_DIR / "AI Wiki"
SOURCES_DIR = WIKI_DIR / "sources"
TOPICS_DIR = WIKI_DIR / "topics"
ENTITIES_DIR = WIKI_DIR / "entities"
INDEX_FILE = WIKI_DIR / "index.md"

ANALYZE_SOURCE_PROMPT = """
Build a clean knowledge base entry from the source.

Rules:
- Deterministic. No fluff.
- Use canonical, widely-used names; reuse instead of inventing.
- Prefer fewer, broader concepts; merge even if slightly imperfect.
- Ground strictly in the source.

Extract:
- summary: 2–3 dense sentences
- key_points: 3–5 atomic facts (non-overlapping)
- topics: ≤3 abstract concepts (broad, reusable)
- entities: ≤3 concrete named things (specific, identifiable)

Topics:
- Must be broad, canonical concepts (1–3 words) that generalize across sources; merge into existing standard terms instead of creating new variations
- Prefer the most general applicable concept (e.g. "Learning" over "Learning Methods" or "Neuroplasticity")
- Always return at least 1 topic

Entities:
- Must be proper nouns or formally named constructs (e.g. "Pomodoro Technique", "Daniel Kahneman")
- Exclude generic concepts or descriptive phrases (these belong to topics)

Source title:
{source_title}

Source content:
{source_content}

Return JSON only:
{{"summary":"...","key_points":["..."],"topics":[{{"name":"...","summary":"..."}}],"entities":[{{"name":"...","summary":"..."}}]}}
"""

llm = ChatOllama(model=MODEL_NAME, temperature=0, format="json")


@dataclass
class RawSource:
    source_path: Path
    source_title: str
    source_slug: str
    source_content: str


@dataclass
class AnalyzedSource:
    raw_source: RawSource
    source_summary: str = ""
    key_points: list[str] = field(default_factory=list)
    topics: list[dict[str, str]] = field(default_factory=list)
    entities: list[dict[str, str]] = field(default_factory=list)


@dataclass
class Mention:
    summary: str
    source_link: str
    source_title: str


@dataclass
class Topic:
    name: str
    mentions: list[Mention] = field(default_factory=list)
    related_entities: set[str] = field(default_factory=set)


@dataclass
class Entity:
    name: str
    mentions: list[Mention] = field(default_factory=list)
    related_topics: set[str] = field(default_factory=set)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.strip() + "\n", encoding="utf-8")


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower().strip())
    return value.strip("-") or "untitled"


def invoke_json(template: str, **kwargs: Any) -> dict[str, Any]:
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | llm
    return json.loads(chain.invoke(kwargs).content)


def get_source_page_path(source_slug: str) -> Path:
    return SOURCES_DIR / f"{source_slug}.md"


def get_topic_page_path(topic_name: str) -> Path:
    return TOPICS_DIR / f"{slugify(topic_name)}.md"


def get_entity_page_path(entity_name: str) -> Path:
    return ENTITIES_DIR / f"{slugify(entity_name)}.md"


def build_wiki_link_target(path: Path) -> str:
    return str(path.relative_to(WIKI_DIR).with_suffix("")).replace("\\", "/")


def build_wiki_link(path: Path) -> str:
    return f"[[{build_wiki_link_target(path)}]]"


def get_unique_lines_in_order(lines: list[str]) -> list[str]:
    return list(dict.fromkeys(line for line in lines if line))


def render_section(title: str, body: str) -> str:
    return f"## {title}\n{body}"


def render_knowledge_page(
    page_name: str,
    mentions: list[Mention],
    related_links: set[str],
) -> str:
    sources = "\n".join(sorted({mention.source_link for mention in mentions}))
    mention_lines = "\n".join(
        get_unique_lines_in_order(
            [f"- {mention.source_link}: {mention.summary}" for mention in mentions]
        )
    )
    related = "\n".join(sorted(related_links))

    return "\n\n".join(
        [
            f"# {page_name}",
            render_section("Sources", sources or "- None yet."),
            render_section("Mentions", mention_lines or "- No source-specific notes yet."),
            render_section("Related", related or "- None yet."),
        ]
    )


def render_index_page(
    source_entries: list[str],
    topic_entries: list[str],
    entity_entries: list[str],
) -> str:
    return "\n\n".join(
        [
            "# Wiki Index",
            render_section("Sources", "\n".join(sorted(set(source_entries))) or "- None yet."),
            render_section("Topics", "\n".join(sorted(set(topic_entries))) or "- None yet."),
            render_section("Entities", "\n".join(sorted(set(entity_entries))) or "- None yet."),
        ]
    )


def clear_generated_wiki() -> None:
    # This example deletes and rebuilds the generated wiki on every run.
    # That is a deliberate simplification for educational purposes.
    # The original LLM Wiki idea is centered on incremental maintenance:
    # the agent should update an existing persistent wiki rather than recreate it from scratch.

    for directory in (SOURCES_DIR, TOPICS_DIR, ENTITIES_DIR):
        if directory.exists():
            shutil.rmtree(directory)

    if INDEX_FILE.exists():
        INDEX_FILE.unlink()


def list_raw_files() -> list[Path]:
    return sorted(RAW_DIR.rglob("*.md"))


def read_source(source_path: Path) -> RawSource:
    content = read_text(source_path)
    return RawSource(
        source_path=source_path,
        source_title=source_path.stem,
        source_slug=slugify(source_path.stem),
        source_content=content,
    )


def analyze_source(raw_source: RawSource) -> AnalyzedSource:
    result = invoke_json(
        ANALYZE_SOURCE_PROMPT,
        source_title=raw_source.source_title,
        source_content=raw_source.source_content,
    )

    return AnalyzedSource(
        raw_source=raw_source,
        source_summary=result.get("summary", ""),
        key_points=result.get("key_points", []),
        topics=result.get("topics", []),
        entities=result.get("entities", []),
    )


def extract_topics_from_source(analyzed_source: AnalyzedSource) -> list[Topic]:
    source_link = build_wiki_link(get_source_page_path(analyzed_source.raw_source.source_slug))
    related_entity_links = [
        f"[[entities/{slugify(item['name'])}]]"
        for item in analyzed_source.entities
    ]
    topics: list[Topic] = []

    for topic in analyzed_source.topics:
        topics.append(
            Topic(
                name=topic["name"],
                mentions=[
                    Mention(
                        summary=topic["summary"],
                        source_link=source_link,
                        source_title=analyzed_source.raw_source.source_title,
                    )
                ],
                related_entities=set(related_entity_links),
            )
        )

    return topics


def extract_entities_from_source(analyzed_source: AnalyzedSource) -> list[Entity]:
    source_link = build_wiki_link(get_source_page_path(analyzed_source.raw_source.source_slug))
    related_topic_links = [
        f"[[topics/{slugify(item['name'])}]]"
        for item in analyzed_source.topics
    ]
    entities: list[Entity] = []

    for entity in analyzed_source.entities:
        entities.append(
            Entity(
                name=entity["name"],
                mentions=[
                    Mention(
                        summary=entity["summary"],
                        source_link=source_link,
                        source_title=analyzed_source.raw_source.source_title,
                    )
                ],
                related_topics=set(related_topic_links),
            )
        )

    return entities


def write_source_page(analyzed_source: AnalyzedSource) -> None:
    current_source_page_path = get_source_page_path(analyzed_source.raw_source.source_slug)
    key_points = "\n".join(f"- {point}" for point in analyzed_source.key_points)
    topics = "\n".join(f"[[topics/{slugify(item['name'])}]]" for item in analyzed_source.topics)
    entities = "\n".join(f"[[entities/{slugify(item['name'])}]]" for item in analyzed_source.entities)

    content = "\n\n".join(
        [
            f"# {analyzed_source.raw_source.source_title}",
            render_section("Summary", analyzed_source.source_summary or "No summary generated."),
            render_section("Key Points", key_points or "- No key points extracted."),
            render_section("Topics", topics or "- None identified."),
            render_section("Entities", entities or "- None identified."),
            render_section("Raw Source", f"- `{analyzed_source.raw_source.source_path.relative_to(OBSIDIAN_DIR)}`"),
        ]
    )

    write_text(current_source_page_path, content)


def merge_topics(topics: list[Topic]) -> dict[str, Topic]:
    merged_topics: dict[str, Topic] = {}

    for topic in topics:
        if topic.name not in merged_topics:
            merged_topics[topic.name] = Topic(name=topic.name)

        merged_topic = merged_topics[topic.name]
        merged_topic.mentions.extend(topic.mentions)
        merged_topic.related_entities.update(topic.related_entities)

    return merged_topics


def merge_entities(entities: list[Entity]) -> dict[str, Entity]:
    merged_entities: dict[str, Entity] = {}

    for entity in entities:
        if entity.name not in merged_entities:
            merged_entities[entity.name] = Entity(name=entity.name)

        merged_entity = merged_entities[entity.name]
        merged_entity.mentions.extend(entity.mentions)
        merged_entity.related_topics.update(entity.related_topics)

    return merged_entities


def write_topic_pages(topics_by_name: dict[str, Topic]) -> list[str]:
    page_entries: list[str] = []
    all_page_links = {name: build_wiki_link(get_topic_page_path(name)) for name in topics_by_name}

    for page_name, topic in sorted(topics_by_name.items()):
        current_page_path = get_topic_page_path(page_name)
        current_link = all_page_links[page_name]
        related_entities = set(topic.related_entities)
        related_entities.discard(current_link)

        page_content = render_knowledge_page(
            page_name=page_name,
            mentions=topic.mentions,
            related_links=related_entities,
        )
        write_text(current_page_path, page_content)
        page_entries.append(f"- {current_link}")

    return page_entries


def write_entity_pages(entities_by_name: dict[str, Entity]) -> list[str]:
    page_entries: list[str] = []
    all_page_links = {name: build_wiki_link(get_entity_page_path(name)) for name in entities_by_name}

    for page_name, entity in sorted(entities_by_name.items()):
        current_page_path = get_entity_page_path(page_name)
        current_link = all_page_links[page_name]
        related_topics = set(entity.related_topics)
        related_topics.discard(current_link)

        page_content = render_knowledge_page(
            page_name=page_name,
            mentions=entity.mentions,
            related_links=related_topics,
        )
        write_text(current_page_path, page_content)
        page_entries.append(f"- {current_link}")

    return page_entries


def write_index_page(
    analyzed_sources: list[AnalyzedSource],
    topic_entries: list[str],
    entity_entries: list[str],
) -> None:
    source_entries = [
        f"- {build_wiki_link(get_source_page_path(analyzed_source.raw_source.source_slug))} - {analyzed_source.source_summary}"
        for analyzed_source in analyzed_sources
    ]
    content = render_index_page(source_entries, topic_entries, entity_entries)
    write_text(INDEX_FILE, content)


def main() -> None:
    clear_generated_wiki()

    source_paths = list_raw_files()
    analyzed_sources: list[AnalyzedSource] = []
    topic_contributions: list[Topic] = []
    entity_contributions: list[Entity] = []

    for source_path in source_paths:
        print(f"Processing {source_path} ...")

        raw_source = read_source(source_path)
        analyzed_source = analyze_source(raw_source)

        analyzed_sources.append(analyzed_source)
        write_source_page(analyzed_source)

        topic_contributions.extend(extract_topics_from_source(analyzed_source))
        entity_contributions.extend(extract_entities_from_source(analyzed_source))

    topics_by_name = merge_topics(topic_contributions)
    entities_by_name = merge_entities(entity_contributions)

    topic_entries = write_topic_pages(topics_by_name)
    entity_entries = write_entity_pages(entities_by_name)

    write_index_page(analyzed_sources, topic_entries, entity_entries)

    print(f"Processed {len(source_paths)} sources.")


if __name__ == "__main__":
    main()
