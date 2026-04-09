# FreshWiki 5-topic Paper-style Tables

This file reports results in a paper-like format using the official FreshWiki outline evaluation metrics from STORM:

- `Heading Soft Recall`
- `Heading Entity Recall`

Evaluation scope:

- Dataset: `FreshWiki`
- Subset: `5-topic subset`
- Topics: `Taylor Hawkins`, `Lahaina, Hawaii`, `Silicon Valley Bank`, `OceanGate`, `Threads (social network)`
- Ground truth: human-written FreshWiki article headings
- Prediction file: `storm_gen_outline.txt`

## Outline Quality

| Method | Heading Soft Recall | Heading Entity Recall |
|---|---:|---:|
| Original STORM | 96.11 | 56.67 |
| storm-langgraph | 85.30 | 36.67 |

## Per-topic Outline Quality

| Topic | System | Heading Soft Recall | Heading Entity Recall |
|---|---|---:|---:|
| Taylor Hawkins | Original STORM | 98.54 | 100.00 |
| Taylor Hawkins | storm-langgraph | 90.76 | 100.00 |
| Lahaina, Hawaii | Original STORM | 90.34 | 0.00 |
| Lahaina, Hawaii | storm-langgraph | 79.71 | 0.00 |
| Silicon Valley Bank | Original STORM | 98.43 | 100.00 |
| Silicon Valley Bank | storm-langgraph | 86.11 | 0.00 |
| OceanGate | Original STORM | 96.86 | 33.33 |
| OceanGate | storm-langgraph | 91.75 | 33.33 |
| Threads (social network) | Original STORM | 96.36 | 50.00 |
| Threads (social network) | storm-langgraph | 78.19 | 50.00 |

## Source Files

- Original STORM outline metrics: `/Users/wangbozhi/Documents/New project/comparison-storm/results/freshwiki_5/storm_outline_quality.csv`
- storm-langgraph outline metrics: `/Users/wangbozhi/Documents/New project/comparison-storm/results/freshwiki_5/storm_langgraph_outline_quality.csv`

## Important Note

These numbers use the same metric definitions as the STORM paper, but they are not a full paper-level reproduction because:

- this is a `5-topic subset`, not the full FreshWiki benchmark
- the model setup is not fully matched to the original paper
- the retrieval setting is your current local-file FreshWiki setup
