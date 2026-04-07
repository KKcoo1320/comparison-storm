# comparison-storm

Minimal comparison workspace for running original STORM and a LangGraph-based STORM variant on the same local topic text.

## What is included

- `scripts/run_storm_wiki_gpt_with_local_file_rm.py`
  - Original STORM entrypoint adapted to use a local topic file retriever.
- `scripts/run_real.py`
  - LangGraph STORM entrypoint for real LLM runs.
- `scripts/real_components.py`
  - Real component adapters for LangGraph STORM, including local-file retrieval support.
- `scripts/compare_outputs.py`
  - Small helper to compare output presence and rough size statistics.
- `results/Taylor_Hawkins_compare.json`
  - Current comparison summary for the `Taylor_Hawkins` topic.
- `results/Taylor_Hawkins_proxy_outline_eval.json`
  - A lightweight proxy evaluation for outline quality on `Taylor_Hawkins`.

## Experiment setup

This comparison was run with both systems consuming the same local file:

- `FreshWiki/txt/Taylor_Hawkins.txt`

That makes the run stable and reproducible, but it also introduces ground-truth leakage. So this setup is useful for engineering comparison and pipeline alignment, not for a strict paper-quality benchmark claim.

## Current comparison snapshot

From `results/Taylor_Hawkins_compare.json`:

- Original STORM produced a longer article and consumed more retrieved evidence.
- LangGraph STORM completed successfully on the same local text, but currently remains lighter-weight than the original pipeline.
- A lightweight proxy outline evaluation shows similar soft heading recall, while original STORM currently retains better heading-level entity coverage on this single topic.

## Current numbers

```json
{
  "topic_name": "Taylor_Hawkins",
  "storm": {
    "article_chars": 9293,
    "outline_exists": true,
    "article_exists": true,
    "search_result_items": 108
  },
  "storm_langgraph": {
    "article_chars": 6493,
    "outline_exists": true,
    "article_exists": true,
    "search_result_items": 18
  }
}
```

## Proxy outline metrics

These are not the original paper's exact 4.4 metric outputs. They are lightweight proxy metrics used because the full original metric stack hit local runtime issues in the current environment.

```json
{
  "topic": "Taylor_Hawkins",
  "proxy_metrics": {
    "storm": {
      "heading_soft_recall_proxy": 0.5023334547203385,
      "heading_entity_recall_proxy": 0.2222222222222222,
      "num_headings": 48
    },
    "storm_langgraph": {
      "heading_soft_recall_proxy": 0.49915638315627203,
      "heading_entity_recall_proxy": 0.1111111111111111,
      "num_headings": 18
    },
    "gold_num_headings": 10
  }
}
```

## Notes

- This repository intentionally stores only the minimal comparison scripts and summary, not full source copies of both upstream projects.
- The scripts assume access to the local source workspaces used during development.
