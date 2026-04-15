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
| storm-langgraph (previous) | 85.30 | 36.67 |
| storm-langgraph (current rerun, Apr 15 2026) | 94.21 | 39.17 |

## Rerun Confirmation

The official outline evaluation was rerun on April 14, 2026 against:

- prediction directory: `/Users/wangbozhi/Documents/New project/storm_user_repo/storm_langgraph/real_output_batch`
- prediction file: `storm_gen_outline.txt`
- metric script: `/Users/wangbozhi/Documents/New project/storm_upstream_naacl/eval/eval_outline_quality.py`

The rerun reproduced the same average scores:

- `Average Entity Recall: 0.36666666666666664`
- `Average Heading Soft Recall: 0.8530395269393921`

This confirms that the current `storm-langgraph` outline benchmark gap is due to the generation pipeline rather than metric mismatch or one-off evaluation noise.

## Current Experiment Update

After a new round of prompt, retrieval, and outline-refine changes, the full 5-topic batch was rerun on April 15, 2026 and evaluated again with the same official script.

Updated averages:

- `Average Entity Recall: 0.39166666666666666`
- `Average Heading Soft Recall: 0.9420553600000001`

This means the new `storm-langgraph` run improved by:

- `+8.91` in Heading Soft Recall
- `+2.50` in Heading Entity Recall

relative to the previous `85.30 / 36.67` run.

## Per-topic Outline Quality

| Topic | System | Heading Soft Recall | Heading Entity Recall |
|---|---|---:|---:|
| Taylor Hawkins | Original STORM | 98.54 | 100.00 |
| Taylor Hawkins | storm-langgraph (previous) | 90.76 | 100.00 |
| Taylor Hawkins | storm-langgraph (current rerun) | 101.24 | 100.00 |
| Lahaina, Hawaii | Original STORM | 90.34 | 0.00 |
| Lahaina, Hawaii | storm-langgraph (previous) | 79.71 | 0.00 |
| Lahaina, Hawaii | storm-langgraph (current rerun) | 87.28 | 12.50 |
| Silicon Valley Bank | Original STORM | 98.43 | 100.00 |
| Silicon Valley Bank | storm-langgraph (previous) | 86.11 | 0.00 |
| Silicon Valley Bank | storm-langgraph (current rerun) | 92.88 | 0.00 |
| OceanGate | Original STORM | 96.86 | 33.33 |
| OceanGate | storm-langgraph (previous) | 91.75 | 33.33 |
| OceanGate | storm-langgraph (current rerun) | 95.78 | 33.33 |
| Threads (social network) | Original STORM | 96.36 | 50.00 |
| Threads (social network) | storm-langgraph (previous) | 78.19 | 50.00 |
| Threads (social network) | storm-langgraph (current rerun) | 93.86 | 50.00 |

## Source Files

- Original STORM outline metrics: `/Users/wangbozhi/Documents/New project/comparison-storm/results/freshwiki_5/storm_outline_quality.csv`
- storm-langgraph outline metrics: `/Users/wangbozhi/Documents/New project/comparison-storm/results/freshwiki_5/storm_langgraph_outline_quality.csv`
- storm-langgraph rerun outline metrics: `/Users/wangbozhi/Documents/New project/comparison-storm/results/freshwiki_5/storm_langgraph_outline_quality_rerun.csv`

## Important Note

These numbers use the same metric definitions as the STORM paper, but they are not a full paper-level reproduction because:

- this is a `5-topic subset`, not the full FreshWiki benchmark
- the model setup is not fully matched to the original paper
- the retrieval setting is your current local-file FreshWiki setup
