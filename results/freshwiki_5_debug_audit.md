# FreshWiki 5-topic Debug Audit for storm-langgraph

This note summarizes the most important implementation drifts between the current `storm-langgraph` setup and the STORM paper pipeline, together with the latest official outline evaluation outputs across two runs.

## Official Outline Evaluation Outputs

### Previous rerun

The following output comes from the earlier rerun of the official FreshWiki outline evaluation script:

```text
2026-04-14 19:24:20,864 SequenceTagger predicts: Dictionary with 20 tags: <unk>, O, S-ORG, S-MISC, B-PER, E-PER, S-LOC, B-ORG, E-ORG, I-PER, S-PER, B-MISC, I-MISC, E-MISC, I-ORG, B-LOC, E-LOC, I-LOC, <START>, <STOP>
'(ReadTimeoutError("HTTPSConnectionPool(host='huggingface.co', port=443): Read timed out. (read timeout=10)"), '(Request ID: 0bbebbcf-bbd5-4500-8ac8-cf1a686de90e)')' thrown while requesting HEAD https://huggingface.co/sentence-transformers/paraphrase-MiniLM-L6-v2/resolve/main/./config_sentence_transformers.json
Retrying in 1s [Retry 1/5].
5it [00:57, 11.49s/it]
Average Entity Recall: 0.36666666666666664
Average Heading Soft Recall: 0.8530395269393921
```

Converted to paper-style percentages:

| Method | Heading Soft Recall | Heading Entity Recall |
|---|---:|---:|
| STORM (paper, GPT-4) | 92.73 | 45.91 |
| storm-langgraph (previous run, FreshWiki 5-topic subset) | 85.30 | 36.67 |

### Current experiment rerun

The latest rerun on April 15, 2026 produced the following per-topic results:

| Topic | Heading Soft Recall | Heading Entity Recall |
|---|---:|---:|
| Taylor Hawkins | 101.24 | 100.00 |
| Lahaina, Hawaii | 87.28 | 12.50 |
| Silicon Valley Bank | 92.88 | 0.00 |
| OceanGate | 95.78 | 33.33 |
| Threads (social network) | 93.86 | 50.00 |

Converted to averaged paper-style percentages:

| Method | Heading Soft Recall | Heading Entity Recall |
|---|---:|---:|
| STORM (paper, GPT-4) | 92.73 | 45.91 |
| storm-langgraph (previous run) | 85.30 | 36.67 |
| storm-langgraph (current rerun, Apr 15 2026) | 94.21 | 39.17 |

This update changes the interpretation of the system:

- the pipeline is no longer clearly behind the paper on structural coverage
- the remaining gap is now concentrated much more on entity-heavy heading coverage
- future optimization should focus primarily on `Heading Entity Recall`

## Step 2: Implementation Drift Checklist

| Item | Current implementation | Paper expectation | Mismatch | More affected metric | Severity |
|---|---|---|---|---|---|
| Related topic generation | Original LangGraph version directly generated personas from topic text without a true related-topic discovery stage. | First find related Wikipedia pages. | Yes | Entity Recall > Soft Recall | High |
| Perspective generation from related page outlines | Original scored version did not derive personas from related page TOCs. | Use related page outlines as inspiration. | Yes | Both | High |
| Basic fact writer | Includes a basic neutral persona. | Paper includes a default basic writer. | No | Both | Low |
| Multi-turn conversation | Multi-turn exists, but the lighter run had fewer perspectives and turns than paper. | Full multi-turn research conversation. | Partial | Both | Medium |
| One-question-at-a-time | Implemented one question at a time. | Same. | No | None | Low |
| History-aware follow-up | History is passed, but prompt pressure for non-redundant follow-up was weaker. | Questions should build on prior QA. | Partial | Entity Recall | Medium |
| Early stopping | No strong early stop in the current graph, but weak prompts can still cause shallow questions. | Stop only after sufficient coverage. | Partial | Entity Recall | Medium |
| Query decomposition | Query generation exists, but older prompt was lightweight and often too close to the raw question. | Decompose questions into search-ready, high-recall queries. | Yes | Entity Recall | High |
| Retrieval quality | Local retriever ranked chunks using weak lexical matching in the scored version. | Retrieval should surface useful evidence across pages. | Yes | Entity Recall > Soft Recall | High |
| Ground-truth leakage | Local retrieval uses the topic's own FreshWiki text file as corpus. | Ground-truth article should be excluded from retrieval. | Yes | Benchmark validity | High |
| Draft + refine outline split | Implemented as two stages. | Same. | No | Both | Low |
| Refine uses conversations | Conversation text is passed into refine. | Same. | No | Both | Low |
| Outline output format | Compatible overall, but generated headings could include numbering or generic noise. | Clean heading-only outline. | Partial | Both | Medium |
| Heading extraction loses hierarchy | Current `# / ## / ###` formatting is compatible with official extraction. | Preserve heading hierarchy. | No | None | Low |
| Eval script consistency | Uses official `eval_outline_quality.py` and `metrics.py`. | Same metric code. | No | None | Low |
| LangGraph orchestration bugs | No strong evidence of state overwrite in the main serial graph. | No such issue. | No | None | Low |
| Token truncation | Several generation steps used relatively tight token limits in the lighter implementation. | Enough room for detailed evidence and outline refinement. | Yes | Entity Recall > Soft Recall | Medium |
| Model/sampling mismatch | Current LLM setup differs from paper's GPT-3.5 / instruct / GPT-4 mix. | Paper uses specific model assignments per stage. | Yes | Both | Medium |
| Prompt wording mismatch | Many prompts are custom LangGraph prompts rather than paper-faithful DSPy prompts. | Closer to original STORM prompting. | Yes | Both | High |
| Weak fallback behavior | JSON fallback and lighter prompts can collapse stages toward weak RAG/direct-gen behavior. | Preserve strong multi-stage research workflow. | Yes | Both | Medium |

## Step 3: Most Likely Reasons for the Current Score Pattern

The previous score pattern `85.30 / 36.67` suggested that the system often got the broad article structure roughly right, but missed topic-specific entities and fine-grained sections.

The current score pattern `94.21 / 39.17` suggests that structure coverage is now strong, while the remaining weakness is concentrated in specific entity surfacing.

### Top 10 likely causes

1. Retrieval ranking is too weak.
Reason:
The outline can still recover generic sections, but long-tail entities and specific events are not reliably surfaced.
How to verify:
Inspect the top retrieved chunks for several turns and check whether they contain the eventual missing entities.
How to fix:
Use stronger chunk scoring or a better retriever, and prefer multi-page retrieval over same-topic local text only.

2. Missing related-topic and TOC inspiration.
Reason:
Without related page structure priors, personas and headings stay generic.
How to verify:
Compare current personas against the original STORM personas and see whether they cover comparable sub-angles.
How to fix:
Generate personas from related page titles and their table of contents.

3. Perspectives are too broad.
Reason:
Soft Recall can remain decent because generic section titles overlap semantically, but Entity Recall drops when headings do not mention specific people, organizations, incidents, or products.
How to verify:
Review generated personas and see whether they sound like broad viewpoints instead of section-worthy editorial agendas.
How to fix:
Rewrite persona prompts to prefer specific, article-structuring perspectives.

4. Conversation depth is insufficient.
Reason:
Shallow multi-turn research leaves obvious section names but fails to collect second-order details.
How to verify:
Count how many later-turn questions introduce new entities rather than rephrasing earlier ones.
How to fix:
Increase perspective count, turn count, and follow-up pressure.

5. Query decomposition is not recall-oriented enough.
Reason:
If queries mostly paraphrase the question, retrieval misses alternate names, incidents, timelines, and aliases.
How to verify:
Read generated queries and look for lack of entity variants or specific event phrasing.
How to fix:
Generate multiple query styles per question and bias toward names, dates, organizations, and controversies.

6. Refine outline does not convert evidence into headings strongly enough.
Reason:
The system may know the facts in conversation but still produce generic headings like `History`, `Impact`, or `Reception`.
How to verify:
Check whether entities appearing in conversation logs are absent from final headings.
How to fix:
Force refine prompts to surface named entities, events, products, organizations, and timelines in section titles.

7. Heading formatting pollution hurts evaluation.
Reason:
Numbered or noisy headings can slightly reduce matching quality even when content is otherwise close.
How to verify:
Open `storm_gen_outline.txt` and look for numbered titles, summaries, conclusions, or references.
How to fix:
Clean headings before serialization.

8. Token budgets are too tight.
Reason:
Short answer or outline generations compress away proper nouns and specifics first.
How to verify:
Check whether generated answers summarize evidence too aggressively.
How to fix:
Increase max tokens for answer synthesis and outline refinement.

9. The retrieval setting does not match the paper.
Reason:
The local-file setup changes the task from web research over related pages to mining the target page text itself.
How to verify:
Swap to a multi-page or search-style corpus and compare behavior.
How to fix:
Build a retrieval corpus over related pages and exclude the target page.

10. Model and prompt stack are not paper-faithful.
Reason:
Even with the same metrics, a different LLM family and different prompts can materially shift heading quality.
How to verify:
Keep the pipeline fixed and only vary draft/refine models or prompt wording.
How to fix:
Align stage-specific models and prompts more closely to the original system.

## Practical Interpretation

The current gap to paper STORM GPT-4 is now:

- Soft Recall: `94.21 - 92.73 = +1.48`
- Entity Recall: `45.91 - 39.17 = 6.74`

This updated gap pattern is more consistent with a pipeline that already generates strong high-level structure but still under-recovers topic-specific entities and fine-grained entity-bearing section titles.

## Most Useful Next Changes

### P0

- Add stronger related-topic and TOC-inspired persona generation.
- Replace weak local chunk ranking with a stronger retriever or better lexical scoring.
- Strengthen outline refine prompts to force entity-rich headings.
- Increase research depth toward paper-like `N=5, M=5`.

### P1

- Expand query decomposition for names, timelines, aliases, and controversies.
- Increase answer and refine token budgets.
- Use a stronger model for draft/refine outline stages.

### P2

- Further polish heading cleanup and serialization.
- Audit any remaining prompt fallback paths.

## Important Reproduction Caveat

Even with the official evaluation script, this is not yet a strict paper-level reproduction because:

- the run is on a `5-topic subset`, not full FreshWiki
- retrieval is a local FreshWiki text setup rather than the paper's search-oriented setting
- stage-specific LLM choices and prompts differ from the original STORM system
- ground-truth exclusion is not faithfully enforced in the current local-file retrieval design
