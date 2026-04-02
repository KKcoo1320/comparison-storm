from __future__ import annotations

import json
from argparse import ArgumentParser
from pathlib import Path


def load_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def count_search_results(conversation_log_path: Path) -> int:
    if not conversation_log_path.exists():
        return 0
    data = json.loads(conversation_log_path.read_text(encoding="utf-8"))
    return sum(len(turn["search_results"]) for item in data for turn in item["dlg_turns"])


def main():
    parser = ArgumentParser()
    parser.add_argument("--topic-name", required=True)
    parser.add_argument("--storm-dir", required=True)
    parser.add_argument("--langgraph-dir", required=True)
    args = parser.parse_args()

    storm_topic_dir = Path(args.storm_dir) / args.topic_name
    langgraph_topic_dir = Path(args.langgraph_dir) / args.topic_name

    storm_article = load_text(storm_topic_dir / "storm_gen_article_polished.txt")
    langgraph_article = load_text(langgraph_topic_dir / "storm_gen_article_polished.txt")

    report = {
        "topic_name": args.topic_name,
        "storm": {
            "article_chars": len(storm_article),
            "outline_exists": (storm_topic_dir / "storm_gen_outline.txt").exists(),
            "article_exists": (storm_topic_dir / "storm_gen_article_polished.txt").exists(),
            "search_result_items": count_search_results(storm_topic_dir / "conversation_log.json"),
        },
        "storm_langgraph": {
            "article_chars": len(langgraph_article),
            "outline_exists": (langgraph_topic_dir / "storm_gen_outline.txt").exists(),
            "article_exists": (langgraph_topic_dir / "storm_gen_article_polished.txt").exists(),
            "search_result_items": count_search_results(langgraph_topic_dir / "conversation_log.json"),
        },
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
