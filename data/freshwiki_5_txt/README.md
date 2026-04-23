# FreshWiki 5-Topic Text Subset

This directory contains the local FreshWiki text subset used by the STORM comparison batch.

## Topics

| Topic | File |
|---|---|
| Taylor Hawkins | `Taylor_Hawkins.txt` |
| Lahaina, Hawaii | `Lahaina,_Hawaii.txt` |
| Silicon Valley Bank | `Silicon_Valley_Bank.txt` |
| OceanGate | `OceanGate.txt` |
| Threads (social network) | `Threads_(social_network).txt` |

## Related Outputs

- Original STORM outputs: `../../results/freshwiki_5/storm/`
- storm-langgraph outputs: `../../results/freshwiki_5/storm_langgraph/`
- Topic metadata: `../../results/freshwiki_5_topics.csv`
- Outline metrics: `../../results/freshwiki_5/storm_outline_quality.csv`
- storm-langgraph outline metrics: `../../results/freshwiki_5/storm_langgraph_outline_quality.csv`
- storm-langgraph rerun metrics: `../../results/freshwiki_5/storm_langgraph_outline_quality_rerun.csv`
- Article auto metrics: `../../results/freshwiki_5/storm_langgraph_article_auto_metrics.csv`

## Notes

This is a small engineering subset rather than the full FreshWiki benchmark. It is intended to make the saved STORM comparison outputs reproducible with the same local input texts.
