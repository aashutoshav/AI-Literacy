# AI Literacy Coding — Results

Best method on the 200-call coding file compiled 2026-10-30 (`data/coding_n200.csv`): **Gemma 4 31B-it, prompt v5, zero-shot**. It scores the AI-related text from executive earnings calls 0–2 on **conceptual, critical, applied, governance**, and is compared with the human codes. Headline numbers are on the **held-out TEST half (100 calls)**, which was not used to write the prompt.

## Model vs human codes — TEST (held-out, n=100)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .476 | .573 | .612 | 66.0% (66/100) |
| Critical | .444 | .507 | .491 | 79.0% (79/100) |
| Applied | .563 | .641 | .665 | 72.0% (72/100) |
| Governance | .470 | .513 | .497 | 89.0% (89/100) |
| Overall four-dimension average | .562 | .757 | .771 | 34.0% (34/100) |

Overall average: ICC(A,1) = **.759** (95% bootstrap CI .651–.837). Mean absolute difference between model and human codes = 0.180 points on the 0–2 scale.

## Model vs human codes — all 200 calls

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .462 | .551 | .564 | 66.5% (133/200) |
| Critical | .421 | .474 | .469 | 79.0% (158/200) |
| Applied | .601 | .675 | .691 | 74.0% (148/200) |
| Governance | .499 | .528 | .547 | 88.5% (177/200) |
| Overall four-dimension average | .553 | .749 | .756 | 35.0% (70/200) |

Overall average: ICC(A,1) = **.750** (95% bootstrap CI .678–.806). Mean absolute difference between model and human codes = 0.185 points on the 0–2 scale.

## Older 143-call file (`data/coding.csv`)

| Best method on this file | Overall-average α, all 143 | Overall-average α, TEST (73) |
|---|---:|---:|
| Gemma 4 12B-it, prompt v4, zero-shot | .711 | .663 |

Prompt v5 does not transfer to this file: the two coding rounds set different bars for a 2 on conceptual and applied (see [EXHAUSTIVE.md §10](EXHAUSTIVE.md)).

## Human benchmark

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .817 | .824 | .848 | 90.5% (38/42) |
| Critical | .700 | .674 | .711 | 83.3% (35/42) |
| Applied | .824 | .806 | .830 | 90.5% (38/42) |
| Governance | .705 | .784 | .751 | 81.0% (34/42) |
| Overall four-dimension average | .738 | .846 | .858 | 61.9% (26/42) |

Overall average: ICC(A,1) = **.849** (95% bootstrap CI .695–.942). Mean absolute difference between coders = 0.143 points on the 0–2 scale.

Note: this is human vs human on 42 cases; the model is scored against the human codes on different cases, so the comparison is indicative, not like-for-like.

## Side by side (model on TEST, n=100)

| Dimension | Model linear κ | Human linear κ | Model α | Human α | Model exact | Human exact |
|---|---:|---:|---:|---:|---:|---:|
| Conceptual | .476 | .817 | .612 | .848 | 66.0% | 90.5% |
| Critical | .444 | .700 | .491 | .711 | 79.0% | 83.3% |
| Applied | .563 | .824 | .665 | .830 | 72.0% | 90.5% |
| Governance | .470 | .705 | .497 | .751 | 89.0% | 81.0% |
| Overall four-dimension average | .562 | .738 | .771 | .858 | 34.0% | 61.9% |

## Methods

- **Model:** Google Gemma 4 instruction-tuned models (12B-it and 31B-it), prompting only, no fine-tuning.
- **Task:** score each call's AI-related sentences 0, 1 or 2 on four dimensions (conceptual, critical, applied, governance), returning JSON with verbatim evidence quotes.
- **Prompt versions:**
  - *Sheet-aligned:* the rubric written to follow the human coding sheet.
  - *v3:* broader governance (security, privacy, risk or oversight connected to AI); stricter critical; multi-area use counted as applied 2.
  - *v4:* v3 with the sheet-aligned applied rule.
  - *v5:* v4 revised from the DEV calls. It uses observed base rates and drops the "when unsure, assign 1" default. A 2 on conceptual or applied is given for specific AI content or uses developed over several statements. Supplying products for AI counts as applied 1. Critical 1 also covers AI-enabled threats and disruption risk.
- **Modes:**
  - *zero-shot:* rubric only;
  - *vote5:* 5 samples, majority per dimension;
  - *few-shot:* 10 worked examples;
  - *ensembles:* per-dimension majority across runs.
- **Evaluation:** each coding file is split into DEV and TEST (stratified, fixed seed). Prompt rules and examples come from DEV only, and TEST is the headline. Model scores are compared with the human codes using the measures below.

## Metrics key

- **Linear weighted κ:** chance-corrected agreement; off by 1 counts half as bad as off by 2. Primary measure.
- **Quadratic weighted κ:** same, but the penalty grows with the square of the distance.
- **Ordinal Krippendorff's α:** chance-corrected reliability for ordered scores.
- **Exact agreement:** share of cases with identical scores (k/n). On the overall row, all four dimensions must match.
- **Overall four-dimension average:** each case's mean of its four scores.
- **ICC(A,1):** absolute agreement on the overall average, single rater.

All runs, splits, ensembles, score distributions, method notes and how to reproduce: [EXHAUSTIVE.md](EXHAUSTIVE.md).
