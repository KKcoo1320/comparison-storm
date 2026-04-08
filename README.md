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
- `results/freshwiki_5_summary.md`
  - A 5-topic comparison summary covering both original STORM and `storm-langgraph`.
- `results/freshwiki_5/`
  - Raw outputs for the 5-topic FreshWiki batch from both systems.

## FreshWiki 5-topic batch

The current multi-topic batch covers:

- `Taylor_Hawkins`
- `Lahaina,_Hawaii`
- `Silicon_Valley_Bank`
- `OceanGate`
- `Threads_(social_network)`

Entry points:

- Summary: `results/freshwiki_5_summary.md`
- Original STORM outputs: `results/freshwiki_5/storm/`
- `storm-langgraph` outputs: `results/freshwiki_5/storm_langgraph/`

Current high-level result:

- Both systems completed all 5 topics.
- In the current configuration, original STORM generated longer articles and more expanded outlines.
- This batch is still not a strict apples-to-apples benchmark because the model configuration was not fully aligned between the two systems.

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

## Suggested experiment tables

### Table 1. Method comparison

Use the same model and the same retriever setting for both systems.

| System | Model | Retriever | Dataset | Heading Soft Recall | Heading Entity Recall | Notes |
|---|---|---|---|---:|---:|---|
| STORM | gpt-4o-mini | local FreshWiki text | FreshWiki subset |  |  | baseline |
| storm-langgraph | gpt-4o-mini | local FreshWiki text | FreshWiki subset |  |  | ours |

### Table 2. Model ablation

Use the same system while changing only the model.

| System | Model | Heading Soft Recall | Heading Entity Recall | Notes |
|---|---|---:|---:|---|
| STORM | gpt-4o-mini |  |  |  |
| STORM | gpt-4o |  |  |  |
| storm-langgraph | gpt-4o-mini |  |  |  |
| storm-langgraph | gpt-4o |  |  |  |

### Single-topic tracking table

Useful before scaling to a multi-topic benchmark.

| Topic | System | Model | Article Chars | Retrieved Items | Heading Soft Recall | Heading Entity Recall |
|---|---|---|---:|---:|---:|---:|
| Taylor Hawkins | STORM | current | 9293 | 108 |  |  |
| Taylor Hawkins | storm-langgraph | current | 6493 | 18 |  |  |

### Important evaluation note

For strict method comparison:

- fix the model
- fix the retriever
- fix the dataset

For model comparison:

- fix the system
- change only the model

Current `Taylor_Hawkins` outline scores in this repository are marked as proxy metrics rather than the paper's exact metric outputs.
