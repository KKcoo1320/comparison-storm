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

## Experiment setup

This comparison was run with both systems consuming the same local file:

- `FreshWiki/txt/Taylor_Hawkins.txt`

That makes the run stable and reproducible, but it also introduces ground-truth leakage. So this setup is useful for engineering comparison and pipeline alignment, not for a strict paper-quality benchmark claim.

## Current comparison snapshot

From `results/Taylor_Hawkins_compare.json`:

- Original STORM produced a longer article and consumed more retrieved evidence.
- LangGraph STORM completed successfully on the same local text, but currently remains lighter-weight than the original pipeline.

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

## Notes

- This repository intentionally stores only the minimal comparison scripts and summary, not full source copies of both upstream projects.
- The scripts assume access to the local source workspaces used during development.
