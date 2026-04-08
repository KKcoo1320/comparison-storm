# FreshWiki 5-topic Summary

## Run status

- Original STORM: 5/5 completed
- `storm-langgraph`: 5/5 completed

Topics:

- `Taylor_Hawkins`
- `Lahaina,_Hawaii`
- `Silicon_Valley_Bank`
- `OceanGate`
- `Threads_(social_network)`

## Important config note

This batch is useful for an engineering comparison, but the model settings are not yet aligned:

- Original STORM used `gpt-3.5-turbo` for conversation plus `gpt-4o` for outline/article/polish.
- `storm-langgraph` was run with `gpt-4o-mini`.

So this should currently be treated as a "current configuration comparison", not a strict apples-to-apples system benchmark.

## Per-topic summary

| Topic | Original STORM total time (s) | Original STORM total time (min) | STORM article chars | LangGraph article chars | STORM search results | LangGraph search results | STORM outline headings | LangGraph outline headings |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `Taylor_Hawkins` | 446.53 | 7.44 | 10156 | 6249 | 108 | 18 | 60 | 23 |
| `Lahaina,_Hawaii` | 268.17 | 4.47 | 13438 | 6674 | 108 | 18 | 60 | 36 |
| `Silicon_Valley_Bank` | 349.51 | 5.83 | 12844 | 6974 | 108 | 18 | 61 | 37 |
| `OceanGate` | 284.32 | 4.74 | 12358 | 6396 | 108 | 18 | 62 | 24 |
| `Threads_(social_network)` | 290.72 | 4.85 | 11348 | 6752 | 108 | 18 | 64 | 28 |

## Aggregate summary

| Metric | Original STORM | `storm-langgraph` | LangGraph / STORM |
|---|---:|---:|---:|
| Completed topics | 5 | 5 | 1.000 |
| Total article chars | 60144 | 33045 | 0.549 |
| Avg article chars / topic | 12028.8 | 6609.0 | 0.549 |
| Total article words | 8805 | 4977 | 0.565 |
| Avg article words / topic | 1761.0 | 995.4 | 0.565 |
| Total search result items | 540 | 90 | 0.167 |
| Avg search result items / topic | 108.0 | 18.0 | 0.167 |
| Total dialog turns | 60 | 30 | 0.500 |
| Avg dialog turns / topic | 12.0 | 6.0 | 0.500 |
| Total outline headings | 307 | 148 | 0.482 |
| Avg outline headings / topic | 61.4 | 29.6 | 0.482 |

## Quick takeaways

1. Both systems finished all 5 topics successfully.
2. In this batch, original STORM produced substantially longer polished articles than `storm-langgraph` on every topic.
3. Original STORM also consumed much more retrieved evidence in the saved conversation logs: `108` search-result items per topic versus `18` for `storm-langgraph`.
4. The generated outlines from original STORM were consistently more expanded, averaging `61.4` heading lines per topic versus `29.6` for `storm-langgraph`.
5. The current gap is likely influenced by both pipeline differences and model mismatch, so this batch is best used as an interim comparison rather than a final benchmark claim.

## Caveats

- Original STORM runtime is available from the captured terminal log above.
- `storm-langgraph` runtime was not persisted into the output artifacts for this batch, so no reliable per-topic time table is included yet for that side.
- Some original STORM runs logged transient network/proxy/SSL warnings while still finishing successfully.

## Output locations

- Original STORM outputs: `/Users/wangbozhi/Documents/New project/comparison-storm/results/freshwiki_5/storm`
- `storm-langgraph` outputs: `/Users/wangbozhi/Documents/New project/storm_user_repo/storm_langgraph/real_output_batch`
