from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests
from openai import OpenAI

from storm_langgraph.text_splitter import split_text
from storm_langgraph.types import Information


def _extract_json_payload(text: str) -> str:
    match = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL)
    if match:
        return match.group(1)
    match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
    if match:
        return match.group(1)
    return text


class OpenAICompatLLM:
    def __init__(self, model: str | None = None):
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY is not set.")
        base_url = os.environ.get("OPENAI_API_BASE") or os.environ.get("AZURE_API_BASE")
        self.model = model or os.environ.get("STORM_LANGGRAPH_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=api_key, base_url=base_url or None)

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float = 0.2,
        max_tokens: int = 800,
    ) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=temperature,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response.choices[0].message.content or ""


@dataclass
class LLMPersonaGenerator:
    llm: OpenAICompatLLM

    def generate_personas(self, topic: str, max_num_persona: int) -> list[str]:
        text = self.llm.complete(
            "You create concise research personas for a long-form grounded writing workflow.",
            (
                f"Topic: {topic}\n"
                f"Return JSON only with schema {{\"personas\": [string, ...]}}.\n"
                f"Generate at most {max_num_persona} personas. Each persona should be a one-line instruction."
            ),
            temperature=0.4,
            max_tokens=300,
        )
        try:
            payload = json.loads(_extract_json_payload(text))
            personas = payload.get("personas", [])
            return [p.strip() for p in personas if isinstance(p, str) and p.strip()][:max_num_persona]
        except Exception:
            lines = [line.strip("- *\n ") for line in text.splitlines() if line.strip()]
            return lines[:max_num_persona]


@dataclass
class LLMQuestionAsker:
    llm: OpenAICompatLLM

    def ask(self, topic: str, persona: str, dialogue_history: list[dict]) -> str:
        history = json.dumps(dialogue_history, ensure_ascii=False)
        return self.llm.complete(
            "You are a Wikipedia writer doing grounded research. Ask one specific next question. If done, say exactly: Thank you so much for your help!",
            (
                f"Topic: {topic}\n"
                f"Persona: {persona}\n"
                f"Recent dialogue history: {history}\n"
                "Return only one question sentence or the exact termination phrase."
            ),
            temperature=0.5,
            max_tokens=120,
        ).strip()


@dataclass
class LLMQueryGenerator:
    llm: OpenAICompatLLM

    def generate_queries(self, topic: str, question: str, max_queries: int) -> list[str]:
        text = self.llm.complete(
            "You turn a research question into web search queries.",
            (
                f"Topic: {topic}\n"
                f"Question: {question}\n"
                f"Return JSON only with schema {{\"queries\": [string, ...]}} and at most {max_queries} queries."
            ),
            temperature=0.2,
            max_tokens=220,
        )
        try:
            payload = json.loads(_extract_json_payload(text))
            queries = payload.get("queries", [])
            return [q.strip() for q in queries if isinstance(q, str) and q.strip()][:max_queries]
        except Exception:
            return [line.strip("- *\n ") for line in text.splitlines() if line.strip()][:max_queries]


class YouRetriever:
    def __init__(self, k: int = 3):
        api_key = os.environ.get("YDC_API_KEY")
        if not api_key:
            raise RuntimeError("YDC_API_KEY is not set.")
        self.api_key = api_key
        self.k = k

    def retrieve(self, queries: list[str], exclude_urls: list[str] | None = None) -> list[Information]:
        exclude_urls = set(exclude_urls or [])
        seen_urls: set[str] = set()
        results: list[Information] = []
        headers = {"X-API-Key": self.api_key}

        for query in queries:
            items: list[dict[str, Any]] = []

            try:
                response = requests.get(
                    "https://api.ydc-index.io/v1/search",
                    headers=headers,
                    params={"query": query, "count": self.k},
                    timeout=20,
                )
                payload = response.json()
                items = (payload.get("results") or {}).get("web") or []
            except Exception:
                items = []

            if not items:
                try:
                    response = requests.get(
                        "https://api.ydc-index.io/search",
                        headers=headers,
                        params={"query": query, "num_web_results": self.k},
                        timeout=20,
                    )
                    payload = response.json()
                    items = payload.get("hits") or []
                except Exception:
                    items = []

            for item in items:
                url = item.get("url")
                if not url or url in exclude_urls or url in seen_urls:
                    continue
                seen_urls.add(url)
                snippets = list(item.get("snippets") or [])
                if not snippets and item.get("description"):
                    snippets = [item["description"]]
                results.append(
                    Information(
                        url=url,
                        title=item.get("title", ""),
                        description=item.get("description", ""),
                        snippets=snippets,
                        meta={},
                    )
                )

        return [
            item for item in results[: self.k * max(1, len(queries))]
        ]


class DuckDuckGoRetriever:
    def __init__(self, k: int = 3):
        from knowledge_storm.rm import DuckDuckGoSearchRM

        self.rm = DuckDuckGoSearchRM(k=k, safe_search="On", region="us-en")

    def retrieve(self, queries: list[str], exclude_urls: list[str] | None = None) -> list[Information]:
        results = self.rm.forward(queries, exclude_urls=exclude_urls or [])
        return [
            Information(
                url=item["url"],
                title=item.get("title", ""),
                description=item.get("description", ""),
                snippets=list(item.get("snippets", [])),
                meta={},
            )
            for item in results
        ]


class LocalTopicFileRetriever:
    def __init__(
        self,
        *,
        topic: str,
        corpus_dir: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
        k: int = 3,
    ):
        self.topic = topic
        self.corpus_dir = Path(corpus_dir)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.k = k

    def _topic_file(self) -> Path:
        topic_name = self.topic.replace(" ", "_").replace("/", "_")
        return self.corpus_dir / f"{topic_name}.txt"

    def retrieve(self, queries: list[str], exclude_urls: list[str] | None = None) -> list[Information]:
        source_file = self._topic_file()
        if not source_file.exists():
            return []

        text = source_file.read_text(encoding="utf-8")
        chunks = split_text(text, chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        if not chunks:
            return []

        def score(chunk: str) -> float:
            chunk_lower = chunk.lower()
            return sum(chunk_lower.count(query.lower().strip()) for query in queries if query.strip())

        ranked_chunks = sorted(chunks, key=score, reverse=True)
        topic_name = self.topic.replace(" ", "_").replace("/", "_")
        return [
            Information(
                url=f"file://{source_file}",
                title=topic_name,
                description=f"Local corpus snippet from {source_file.name}",
                snippets=[chunk],
                meta={"source": "local_topic_file", "query_count": len(queries)},
            )
            for chunk in ranked_chunks[: self.k]
        ]


@dataclass
class LLMAnswerSynthesizer:
    llm: OpenAICompatLLM

    def answer(self, topic: str, question: str, gathered_info: list[Information]) -> str:
        evidence_lines: list[str] = []
        for idx, info in enumerate(gathered_info[:5], start=1):
            snippets = " ".join(info.snippets[:2])
            evidence_lines.append(f"[{idx}] {info.title} | {info.url}\n{snippets}")
        evidence = "\n\n".join(evidence_lines)
        return self.llm.complete(
            "You are a grounded topic expert. Answer only from the provided evidence and be concise.",
            f"Topic: {topic}\nQuestion: {question}\nEvidence:\n{evidence}",
            temperature=0.2,
            max_tokens=220,
        ).strip()


@dataclass
class LLMOutlineGenerator:
    llm: OpenAICompatLLM

    def generate_direct_outline(self, topic: str) -> str:
        return self.llm.complete(
            "You write concise Wikipedia-style outlines. Return markdown headings only.",
            f"Topic: {topic}\nWrite a direct outline with top-level and second-level headings only.",
            temperature=0.3,
            max_tokens=350,
        ).strip()

    def refine_outline(self, topic: str, conversation_text: str, draft_outline: str) -> str:
        return self.llm.complete(
            "You refine an article outline using grounded research notes. Return markdown headings only.",
            (
                f"Topic: {topic}\n"
                f"Draft outline:\n{draft_outline}\n\n"
                f"Research conversation:\n{conversation_text}\n\n"
                "Produce a better outline with clear section hierarchy."
            ),
            temperature=0.3,
            max_tokens=500,
        ).strip()


@dataclass
class LLMSectionWriter:
    llm: OpenAICompatLLM

    def write_section(
        self,
        topic: str,
        section_name: str,
        section_outline: str,
        collected_info: list[Information],
    ) -> str:
        info_chunks: list[str] = []
        for idx, info in enumerate(collected_info[:6], start=1):
            info_chunks.append(f"[{idx}] {info.title}\n" + "\n".join(info.snippets[:2]))
        evidence = "\n\n".join(info_chunks)
        return self.llm.complete(
            "You write one Wikipedia-style section with inline citations like [1][2]. Start with a markdown heading for the section and do not write other sections.",
            (
                f"Topic: {topic}\n"
                f"Section: {section_name}\n"
                f"Section outline:\n{section_outline}\n\n"
                f"Evidence:\n{evidence}"
            ),
            temperature=0.3,
            max_tokens=900,
        ).strip()


@dataclass
class LLMArticlePolisher:
    llm: OpenAICompatLLM

    def write_lead(self, topic: str, draft_article: str) -> str:
        return self.llm.complete(
            "You write a short encyclopedia lead summarizing the article.",
            f"Topic: {topic}\nDraft article:\n{draft_article}\n\nWrite a 2-4 sentence lead.",
            temperature=0.2,
            max_tokens=220,
        ).strip()

    def deduplicate(self, draft_article: str) -> str:
        return self.llm.complete(
            "You remove repeated content while preserving structure and citations.",
            f"Article:\n{draft_article}\n\nReturn the cleaned article only.",
            temperature=0.0,
            max_tokens=1200,
        ).strip()
