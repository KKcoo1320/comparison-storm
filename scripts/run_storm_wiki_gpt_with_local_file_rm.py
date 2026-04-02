"""
STORM Wiki pipeline powered by GPT models and a local topic file retriever.

This script is intended for stable local experiments where both original STORM
and storm-langgraph consume the same local text file as retrieval corpus.
"""

import os
import re
from argparse import ArgumentParser
from pathlib import Path

import dspy

from knowledge_storm import (
    STORMWikiRunnerArguments,
    STORMWikiRunner,
    STORMWikiLMConfigs,
)
from knowledge_storm.lm import OpenAIModel, AzureOpenAIModel
from knowledge_storm.utils import load_api_key


SEPARATORS = ["\n\n", "\n", ".", ",", " ", ""]


def split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    text = text or ""
    if len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        candidate = text[start:end]
        split_point = None
        for separator in SEPARATORS:
            if not separator:
                continue
            idx = candidate.rfind(separator)
            if idx > chunk_size // 3:
                split_point = start + idx + len(separator)
                break
        final_end = split_point or end
        chunk = text[start:final_end].strip()
        if chunk:
            chunks.append(chunk)
        if final_end >= len(text):
            break
        start = max(start + 1, final_end - chunk_overlap)
    return chunks


class LocalTopicFileRM(dspy.Retrieve):
    def __init__(
        self,
        topic: str,
        corpus_dir: str,
        k: int = 3,
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ):
        super().__init__(k=k)
        self.topic = topic
        self.corpus_dir = Path(corpus_dir)
        self.k = k
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.usage = 0

    def get_usage_and_reset(self):
        usage = self.usage
        self.usage = 0
        return {"LocalTopicFileRM": usage}

    def _topic_file(self) -> Path:
        topic_name = self.topic.replace(" ", "_").replace("/", "_")
        return self.corpus_dir / f"{topic_name}.txt"

    def forward(self, query_or_queries, exclude_urls=None):
        queries = [query_or_queries] if isinstance(query_or_queries, str) else query_or_queries
        self.usage += len(queries)

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
        title = source_file.stem
        return [
            {
                "url": f"file://{source_file}",
                "title": title,
                "description": f"Local corpus snippet from {source_file.name}",
                "snippets": [chunk],
            }
            for chunk in ranked_chunks[: self.k]
        ]


def main(args):
    load_api_key(toml_file_path="secrets.toml")
    lm_configs = STORMWikiLMConfigs()
    openai_kwargs = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "api_base": os.getenv("OPENAI_API_BASE"),
        "temperature": 1.0,
        "top_p": 0.9,
    }

    ModelClass = (
        OpenAIModel if os.getenv("OPENAI_API_TYPE") == "openai" else AzureOpenAIModel
    )
    gpt_35_model_name = (
        "gpt-3.5-turbo" if os.getenv("OPENAI_API_TYPE") == "openai" else "gpt-35-turbo"
    )
    gpt_4_model_name = "gpt-4o"
    if os.getenv("OPENAI_API_TYPE") == "azure":
        openai_kwargs["api_base"] = os.getenv("AZURE_API_BASE")
        openai_kwargs["api_version"] = os.getenv("AZURE_API_VERSION")

    conv_simulator_lm = ModelClass(model=gpt_35_model_name, max_tokens=500, **openai_kwargs)
    question_asker_lm = ModelClass(model=gpt_35_model_name, max_tokens=500, **openai_kwargs)
    outline_gen_lm = ModelClass(model=gpt_4_model_name, max_tokens=400, **openai_kwargs)
    article_gen_lm = ModelClass(model=gpt_4_model_name, max_tokens=700, **openai_kwargs)
    article_polish_lm = ModelClass(model=gpt_4_model_name, max_tokens=4000, **openai_kwargs)

    lm_configs.set_conv_simulator_lm(conv_simulator_lm)
    lm_configs.set_question_asker_lm(question_asker_lm)
    lm_configs.set_outline_gen_lm(outline_gen_lm)
    lm_configs.set_article_gen_lm(article_gen_lm)
    lm_configs.set_article_polish_lm(article_polish_lm)

    engine_args = STORMWikiRunnerArguments(
        output_dir=args.output_dir,
        max_conv_turn=args.max_conv_turn,
        max_perspective=args.max_perspective,
        search_top_k=args.search_top_k,
        max_thread_num=args.max_thread_num,
        retrieve_top_k=args.retrieve_top_k,
    )

    topic = args.topic
    rm = LocalTopicFileRM(
        topic=topic,
        corpus_dir=args.corpus_dir,
        k=engine_args.search_top_k,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )

    runner = STORMWikiRunner(engine_args, lm_configs, rm)
    runner.run(
        topic=topic,
        do_research=args.do_research,
        do_generate_outline=args.do_generate_outline,
        do_generate_article=args.do_generate_article,
        do_polish_article=args.do_polish_article,
        remove_duplicate=args.remove_duplicate,
    )
    runner.post_run()
    runner.summary()


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--topic", type=str, required=True, help="Topic to run.")
    parser.add_argument(
        "--corpus-dir",
        type=str,
        default="/Users/wangbozhi/Documents/New project/storm_upstream_naacl/FreshWiki/txt",
        help="Directory containing local topic txt files.",
    )
    parser.add_argument("--output-dir", type=str, default="./results/local_file")
    parser.add_argument("--max-thread-num", type=int, default=3)
    parser.add_argument("--do-research", action="store_true")
    parser.add_argument("--do-generate-outline", action="store_true")
    parser.add_argument("--do-generate-article", action="store_true")
    parser.add_argument("--do-polish-article", action="store_true")
    parser.add_argument("--remove-duplicate", action="store_true")
    parser.add_argument("--max-conv-turn", type=int, default=3)
    parser.add_argument("--max-perspective", type=int, default=3)
    parser.add_argument("--search-top-k", type=int, default=3)
    parser.add_argument("--retrieve-top-k", type=int, default=3)
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=100)
    main(parser.parse_args())
