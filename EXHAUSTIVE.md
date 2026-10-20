# AI Literacy Coding — Exhaustive Results

**What this file is.** The full record behind `RESULTS.md`: every run (Round 2b loosened prompt and sheet-aligned prompt; Gemma 4 12B-it and 31B-it; zero-shot and few-shot×10), per-run agreement tables, exact / adjacent / QWK tables, confusion counts, job metadata, the composite-metric method, notes, conclusions, and how to reproduce. Section 8 adds the 2026-10-19 experiments (per-dimension prompts, 5-sample voting, boundary few-shot, prompt v3). `RESULTS.md` shows only the best run by mean linear κ (prompt v3, Gemma 4 12B-it, 5-sample vote, job 6392418).

The original summary from the top of `RESULTS.md`, kept here verbatim:

> **What this file is.** This project uses an instruction-tuned LLM (Google Gemma 4, 12B and 31B, run on Georgia Tech PACE H200 GPUs) to code the AI-related sentences from earnings calls on four AI-literacy dimensions: **conceptual, critical, applied, governance**, each scored **0, 1 or 2**. This file reports how closely the model's scores agree with the **human codes in `data/coding.csv`** (143 calls, exported from `Training_Compiled_9-28-2026.xlsx`, sheet *Coding*). The best run is **Gemma 4 12B zero-shot with the sheet-aligned prompt (job 6052529)**. Its linear weighted κ is .526 / .488 / .492 / .379 (conceptual / critical / applied / governance), against .817 / .700 / .824 / .705 between the two human coders. Its exact agreement is 81.1% / 76.9% / 73.4% / 74.8%, against 90.5% / 83.3% / 90.5% / 81.0% for the humans. **Takeaway:** the model is usually within one point of the human codes, but after chance correction its agreement is moderate (κ about .38–.53). That is clearly below the human–human benchmark on every dimension, and furthest below on governance and applied.
>
> All numbers below come from files in this repo. Nothing is committed until reviewed.

## Contents

1. Human benchmark (human vs human)
2. Model vs human codes — agreement in the same format
3. What changed between Round 2b and sheet-aligned
4. Detailed run logs (exact / adjacent / QWK / confusion counts)
5. Metrics glossary
6. Conclusions and next steps
7. How to reproduce
8. Experiments of 2026-10-19 (per-dimension, voting, boundary few-shot, prompt v3)

## 1. Human benchmark (human vs human)

Source: the advisor's inter-rater assessment, **Dr. Lee vs Elsie, 42 overlapping cases**, Lee's ratings from "Coding (2)" and Elsie's from "Extra Coding (2)" (including Elsie's four added cases TR265, TR269, TR276, TR297). **Strategic is excluded throughout.** Quoted as sent:

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .817 | .824 | .848 | 90.5% (38/42) |
| Critical | .700 | .674 | .711 | 83.3% (35/42) |
| Applied | .824 | .806 | .830 | 90.5% (38/42) |
| Governance | .705 | .784 | .751 | 81.0% (34/42) |
| Overall four-dimension average | .738 | .846 | .858 | 61.9% (26/42) |

- Linear weighted κ is the primary dimension-level measure, for consistency with the earlier assessment.
- For the overall average, the absolute-agreement, single-measure ICC(A,1) is **.849** (95% bootstrap CI .695–.942). The mean absolute difference between coders is **0.143** points on the 0–2 scale.
- Exact agreement for the overall row means all four dimensions match on a case. This is the same thing this file calls **joint exact**.
- The advisor notes these are preliminary. Critical and Governance only narrowly meet .70, and Critical's quadratic κ is .674.

**Important:** this benchmark is **human vs human on 42 cases**. The model numbers below are **model vs the human codes in `data/coding.csv` on 143 cases** (133 for few-shot runs). The case sets and the comparison partner differ, so side-by-side comparisons are indicative, not a formal test.

## 2. Model vs human codes — agreement in the same format

Computed with `src/agreement.py` (see section 7). Each table uses the advisor's columns. In every run, every prediction was a valid 0/1/2 on all four dimensions, so **0 rows were dropped**. Few-shot runs have n=133 because the 10 exemplars shown in the prompt are held out.

**How the "Overall four-dimension average" row is computed here.** The advisor did not specify her exact method, so this is what we did:

- For each case, the composite is the mean of the four dimension scores, which takes values 0, 0.25, …, 2. This is computed once for the human codes and once for the model.
- **Linear and quadratic κ:** the composite is mapped to 9 ordered categories (composite × 4 → 0…8), and then weighted Cohen's κ is computed over those 9 categories.
- **Ordinal Krippendorff's α:** computed over the 9 composite values, with the value domain fixed at 0, 0.25, …, 2. Interval α is also reported, labeled, in the line under each table.
- **Exact:** all four dimensions match on the case (joint exact), shown as k/n.
- **ICC(A,1):** two-way random effects, absolute agreement, single measure (McGraw & Wong), on the composite with 2 raters (human, model). The 95% CI is a percentile bootstrap over cases, with 2000 resamples and numpy seed 20261019. The direct formula was checked against `pingouin.intraclass_corr` (ICC(A,1)) and matches it.
- **Mean absolute difference:** the mean over cases of |human composite − model composite|.

### 2a. Headline: best run vs the human benchmark

Best run by mean linear κ: **prompt v3, Gemma 4 12B-it, 5-sample vote, job 6392418, n=143** (section 8). The previous best, sheet-aligned 12B zero-shot (job 6052529), is in 2c.

| Dimension | Human–human linear κ | Model linear κ | Human–human ordinal α | Model ordinal α | Human–human exact | Model exact |
|---|---:|---:|---:|---:|---:|---:|
| Conceptual | .817 | .568 | .848 | .603 | 90.5% (38/42) | 82.5% (118/143) |
| Critical | .700 | .542 | .711 | .569 | 83.3% (35/42) | 80.4% (115/143) |
| Applied | .824 | .365 | .830 | .373 | 90.5% (38/42) | 55.9% (80/143) |
| Governance | .705 | .633 | .751 | .658 | 81.0% (34/42) | 82.5% (118/143) |
| Overall four-dimension average | .738 | .516 | .858 | .683 | 61.9% (26/42) | 29.4% (42/143) |
| Composite ICC(A,1) [95% CI] | .849 [.695–.942] | .744 [.643–.816] | | | | |
| Composite mean absolute difference | 0.143 | 0.206 | | | | |

Every model linear κ is below the human–human value.
- **Governance:** the gap is smallest here (.633 vs .705), and model exact agreement is slightly above the human–human figure (82.5% vs 81.0%).
- **Applied:** the gap is largest here (.365 vs .824, exact 55.9% vs 90.5%). Prompt v3 over-scores applied 2 (human 1 scored 2 on 48 calls).
- **Joint exact:** 29.4% vs 61.9%.

### 2b. All runs at a glance (linear weighted κ, the primary measure)

| Run | n | Linear κ conceptual | Linear κ critical | Linear κ applied | Linear κ governance | Mean of 4 linear κ | Composite ICC(A,1) | Joint exact |
|---|--:|---:|---:|---:|---:|---:|---:|---:|
| Sheet-aligned · 12B-it zero-shot · job 6052529 | 143 | .526 | .488 | .492 | .379 | .472 | .701 | 42.7% |
| Sheet-aligned · 12B-it few-shot×10 · job 6052530 | 133 | .236 | .464 | .552 | .257 | .377 | .624 | 23.3% |
| Sheet-aligned · 31B-it zero-shot · job 6052531 | 143 | .451 | .500 | .515 | .364 | .457 | .656 | 39.9% |
| Sheet-aligned · 31B-it few-shot×10 · job 6052532 | 133 | .335 | .521 | .454 | .258 | .392 | .623 | 33.8% |
| Sheet-aligned · 12B-it per-dimension · job 6392317 | 143 | .528 | .432 | .372 | .361 | .423 | .671 | 34.3% |
| Sheet-aligned · 12B-it 5-sample vote · job 6392318 | 143 | .495 | .488 | .504 | .392 | .470 | .712 | 42.0% |
| Sheet-aligned · 12B-it per-dimension + 5-sample vote · job 6392319 | 143 | .528 | .422 | .378 | .374 | .425 | .674 | 35.7% |
| Sheet-aligned · 12B-it boundary few-shot×10 · job 6392320 | 133 | .481 | .431 | .528 | .550 | .497 | .775 | 30.1% |
| Prompt v3 · 12B-it zero-shot · job 6392416 | 143 | .547 | .491 | .365 | .633 | .509 | .731 | 29.4% |
| Prompt v3 · 12B-it per-dimension · job 6392417 | 143 | .466 | .472 | .386 | .728 | .513 | .723 | 30.8% |
| **Prompt v3 · 12B-it 5-sample vote · job 6392418** | **143** | **.568** | **.542** | **.365** | **.633** | **.527** | **.744** | **29.4%** |
| *Human vs human (Lee vs Elsie)* | *42* | *.817* | *.700* | *.824* | *.705* | *.762* | *.849* | *61.9%* |
| Round 2b (loosened) · 12B-it zero-shot · job 6050888 | 143 | .465 | .425 | .365 | .491 | .436 | .741 | 28.7% |
| Round 2b (loosened) · 12B-it few-shot×10 · job 6050889 | 133 | .260 | .427 | .390 | .412 | .372 | .721 | 15.0% |
| Round 2b (loosened) · 31B-it zero-shot · job 6050890 | 143 | .423 | .461 | .434 | .413 | .433 | .707 | 32.2% |
| Round 2b (loosened) · 31B-it few-shot×10 · job 6050891 | 133 | .301 | .510 | .483 | .397 | .423 | .717 | 24.1% |

The human row's "mean of 4 linear κ" (.762) is computed here from the advisor's four values; the advisor did not report it. Interval α and the ICC confidence intervals for each run are in 2c.

### 2c. Per-run tables

#### Sheet-aligned prompt · 12B-it zero-shot · job 6052529 · n=143

Predictions: `outputs/preds_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_sheetalign_zeroshot_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .526 | .545 | .560 | 81.1% (116/143) |
| Critical | .488 | .509 | .526 | 76.9% (110/143) |
| Applied | .492 | .553 | .524 | 73.4% (105/143) |
| Governance | .379 | .462 | .408 | 74.8% (107/143) |
| Overall four-dimension average | .514 | .699 | .666 | 42.7% (61/143) |

Composite: ICC(A,1) = **.701** (95% bootstrap CI .594–.783). Interval α = .696. Mean absolute difference between model and human codes = 0.191 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Sheet-aligned prompt · 12B-it few-shot×10 · job 6052530 · n=133

Predictions: `outputs/preds_fewshot10_12b_n143.csv` · JSON: `outputs/metrics/agreement_sheetalign_fewshot10_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .236 | .384 | .336 | 53.4% (71/133) |
| Critical | .464 | .510 | .490 | 78.2% (104/133) |
| Applied | .552 | .616 | .614 | 72.2% (96/133) |
| Governance | .257 | .270 | .238 | 74.4% (99/133) |
| Overall four-dimension average | .399 | .623 | .582 | 23.3% (31/133) |

Composite: ICC(A,1) = **.624** (95% bootstrap CI .514–.715). Interval α = .599. Mean absolute difference between model and human codes = 0.258 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Sheet-aligned prompt · 31B-it zero-shot · job 6052531 · n=143

Predictions: `outputs/preds_zeroshot_31b_n143.csv` · JSON: `outputs/metrics/agreement_sheetalign_zeroshot_31b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .451 | .471 | .480 | 79.0% (113/143) |
| Critical | .500 | .551 | .536 | 79.7% (114/143) |
| Applied | .515 | .571 | .544 | 74.8% (107/143) |
| Governance | .364 | .403 | .390 | 76.2% (109/143) |
| Overall four-dimension average | .450 | .654 | .613 | 39.9% (57/143) |

Composite: ICC(A,1) = **.656** (95% bootstrap CI .557–.733). Interval α = .641. Mean absolute difference between model and human codes = 0.203 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Sheet-aligned prompt · 31B-it few-shot×10 · job 6052532 · n=133

Predictions: `outputs/preds_fewshot10_31b_n143.csv` · JSON: `outputs/metrics/agreement_sheetalign_fewshot10_31b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .335 | .424 | .421 | 67.7% (90/133) |
| Critical | .521 | .558 | .552 | 80.5% (107/133) |
| Applied | .454 | .507 | .485 | 69.2% (92/133) |
| Governance | .258 | .335 | .226 | 72.9% (97/133) |
| Overall four-dimension average | .423 | .622 | .604 | 33.8% (45/133) |

Composite: ICC(A,1) = **.623** (95% bootstrap CI .524–.704). Interval α = .600. Mean absolute difference between model and human codes = 0.227 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Round 2b loosened prompt · 12B-it zero-shot · job 6050888 · n=143

Predictions: `outputs/round2b_loosened/preds_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_round2b_zeroshot_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .465 | .494 | .509 | 78.3% (112/143) |
| Critical | .425 | .479 | .480 | 72.0% (103/143) |
| Applied | .365 | .462 | .395 | 59.4% (85/143) |
| Governance | .491 | .603 | .527 | 76.9% (110/143) |
| Overall four-dimension average | .529 | .740 | .696 | 28.7% (41/143) |

Composite: ICC(A,1) = **.741** (95% bootstrap CI .652–.812). Interval α = .740. Mean absolute difference between model and human codes = 0.198 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Round 2b loosened prompt · 12B-it few-shot×10 · job 6050889 · n=133

Predictions: `outputs/round2b_loosened/preds_fewshot10_12b_n143.csv` · JSON: `outputs/metrics/agreement_round2b_fewshot10_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .260 | .379 | .340 | 56.4% (75/133) |
| Critical | .427 | .464 | .451 | 73.7% (98/133) |
| Applied | .390 | .494 | .413 | 59.4% (79/133) |
| Governance | .412 | .514 | .482 | 75.9% (101/133) |
| Overall four-dimension average | .460 | .719 | .698 | 15.0% (20/133) |

Composite: ICC(A,1) = **.721** (95% bootstrap CI .638–.783). Interval α = .719. Mean absolute difference between model and human codes = 0.231 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Round 2b loosened prompt · 31B-it zero-shot · job 6050890 · n=143

Predictions: `outputs/round2b_loosened/preds_zeroshot_31b_n143.csv` · JSON: `outputs/metrics/agreement_round2b_zeroshot_31b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .423 | .466 | .467 | 76.2% (109/143) |
| Critical | .461 | .474 | .501 | 76.9% (110/143) |
| Applied | .434 | .516 | .491 | 65.7% (94/143) |
| Governance | .413 | .490 | .481 | 76.2% (109/143) |
| Overall four-dimension average | .494 | .706 | .720 | 32.2% (46/143) |

Composite: ICC(A,1) = **.707** (95% bootstrap CI .626–.769). Interval α = .706. Mean absolute difference between model and human codes = 0.199 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Round 2b loosened prompt · 31B-it few-shot×10 · job 6050891 · n=133

Predictions: `outputs/round2b_loosened/preds_fewshot10_31b_n143.csv` · JSON: `outputs/metrics/agreement_round2b_fewshot10_31b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .301 | .421 | .402 | 60.9% (81/133) |
| Critical | .510 | .533 | .555 | 78.9% (105/133) |
| Applied | .483 | .576 | .544 | 66.9% (89/133) |
| Governance | .397 | .493 | .451 | 75.9% (101/133) |
| Overall four-dimension average | .491 | .716 | .708 | 24.1% (32/133) |

Composite: ICC(A,1) = **.717** (95% bootstrap CI .625–.783). Interval α = .709. Mean absolute difference between model and human codes = 0.218 points on the 0–2 scale. Rows dropped as invalid: 0.

**The composite does not rank runs the same way as the per-dimension measures.** Round 2b runs have a higher composite ICC (.707–.741) than sheet-aligned runs (.623–.701), even though their per-dimension exact and linear κ are mostly lower. One possible reason is that errors in opposite directions on different dimensions cancel in a mean of four scores, but that has not been checked. Per-dimension linear κ is the primary measure, as in the advisor's assessment.

**Check against `src.validate`.** For all eight runs, the quadratic κ, exact agreement and joint exact from `src.agreement` match the existing `src.validate` metrics JSONs exactly (`outputs/metrics/sheetalign_*.json` for sheet-aligned, `outputs/metrics/{zeroshot,fewshot10}_{12b,31b}_n143.json` for Round 2b). That match is also what confirms the files in `outputs/round2b_loosened/` are the Round 2b predictions.

## 3. What changed between Round 2b and sheet-aligned

Both rounds use the same human codes (`data/coding.csv`, 143 calls), the same models (`google/gemma-4-12B-it`, `google/gemma-4-31B-it`), the same four dimensions and 0–2 scale, and the same zero-shot (n=143) / few-shot×10 (n=133) split. Only the prompt changed.

- **Round 2b (loosened prompt):** only conceptual was loosened, so a 1 means any real AI capability, not only a technical mechanism. Everything else still followed the stricter written coding guide.
- **Sheet-aligned prompt:** the coder is told to **match the human coding sheet when the written guide disagrees**. Applied 2 now requires depth, scale, integration, or a measured outcome, and a plain stated use stays 1 ("between 1 and 2, assign 1"). The few-shot exemplar notes were fixed to match the sheet (for example TR009 conceptual 1, TR163 critical 0).

The written rubric is still in the prompt in both rounds.

## 4. Detailed run logs

These are the original per-run records: exact, adjacent, quadratic weighted κ (QWK), joint exact, and the two confusion counts we tracked. Historical figures are unchanged.

### Shared setup

- The human codes are in `data/coding.csv` from `Training_Compiled_9-28-2026.xlsx` (143 calls).
- **Models:** `google/gemma-4-12B-it` and `google/gemma-4-31B-it` on PACE ICE (NVIDIA H200).
- **Zero-shot** scores all 143 calls. **Few-shot ×10** holds out the 10 exemplars in `configs/fewshot_exemplars.json`, so n=133.
- **Agreement** is with the human codes in `data/coding.csv`, not with the written coding guide where the two disagree.
- Earlier runs used a smaller 85-row coding file (now archived) and then one strict-prompt 12B few-shot pass on the new sheet. Those numbers are not comparable to the current `data/coding.csv` results and are not reported here. The strict-prompt prediction file (job 6049275) was overwritten by job 6050889, so it cannot be re-scored from the current CSV.
- Exact rates are rounded to one decimal. Few-shot rows are not the same n as zero-shot rows (133 vs 143).

### Round 2b — loosened conceptual prompt (jobs 6050888–6050891; zero-shot n=143, few-shot n=133)

The prediction CSVs named in this section were overwritten on the cluster by sheet-aligned jobs 6052529–6052532 (same filenames). Local copies at those paths were replaced by rsync on 2026-10-03. The pre-overwrite local files are in `outputs/round2b_loosened/`. The numbers below are the historical writeup and were not recomputed. The Round 2b metrics JSON files were not overwritten. Re-scoring `outputs/round2b_loosened/` with `src.agreement` reproduces these exact and QWK values exactly.

#### Round 2b comparison — exact agreement (loosened prompt; zero-shot n=143, few-shot n=133)

| Job | Model | Prompt | n | Exact conceptual | Exact critical | Exact applied | Exact governance | Joint exact |
|-----|-------|--------|--:|-----------------:|---------------:|--------------:|-----------------:|------------:|
| 6050888 | 12B-it | zero-shot | 143 | 78.3% | 72.0% | 59.4% | 76.9% | 28.7% |
| 6050889 | 12B-it | few-shot×10 | 133 | 56.4% | 73.7% | 59.4% | 75.9% | 15.0% |
| **6050890** | **31B-it** | **zero-shot** | **143** | 76.2% | 76.9% | **65.7%** | 76.2% | **32.2%** |
| 6050891 | 31B-it | few-shot×10 | 133 | 60.9% | 78.9% | 66.9% | 75.9% | 24.1% |

#### Round 2b · loosened prompt · 12B-it zero-shot · n=143 — job 6050888

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 00:33 ET |
| **Elapsed** | 36:53 |
| **Exit** | 0 |
| **Model** | `google/gemma-4-12B-it` |
| **Prompt** | Loosened rubric, zero-shot |
| **Data** | `data/coding.csv`, n=143 |
| **Job** | Slurm `6050888`, PACE ICE H200 |
| **Preds** | `outputs/preds_zeroshot_12b_n143.csv` |
| **Metrics** | `outputs/metrics/zeroshot_12b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 78.3% | 100% | 0.494 |
| critical | 72.0% | 97.9% | 0.479 |
| applied | 59.4% | 100% | 0.462 |
| governance | 76.9% | 100% | 0.603 |
| **joint (all 4)** | **28.7%** | — | — |

Conceptual human code 1 → pred 0: **4** rows. Applied human code 1 → pred 2: **43** rows.

#### Round 2b · loosened prompt · 12B-it few-shot×10 · n=133 — job 6050889

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 00:31 ET |
| **Elapsed** | 35:22 |
| **Model** | `google/gemma-4-12B-it` |
| **Prompt** | Loosened rubric + 10 calibration exemplars (held out) |
| **Data** | `data/coding.csv`, n=133 (143 − 10 exemplars) |
| **Job** | Slurm `6050889`, PACE ICE H200 |
| **Preds** | `outputs/preds_fewshot10_12b_n143.csv` |
| **Metrics** | `outputs/metrics/fewshot10_12b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 56.4% | 99.2% | 0.379 |
| critical | 73.7% | 99.2% | 0.464 |
| applied | 59.4% | 100% | 0.494 |
| governance | 75.9% | 100% | 0.514 |
| **joint (all 4)** | **15.0%** | — | — |

Conceptual human code 1 → pred 0: **33** rows. Applied human code 1 → pred 2: **40** rows.

#### Round 2b · loosened prompt · 31B-it zero-shot · n=143 — job 6050890

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 00:41 ET |
| **Elapsed** | 44:47 |
| **Model** | `google/gemma-4-31B-it` |
| **Prompt** | Loosened rubric, zero-shot |
| **Data** | `data/coding.csv`, n=143 |
| **Job** | Slurm `6050890`, PACE ICE H200 |
| **Preds** | `outputs/preds_zeroshot_31b_n143.csv` |
| **Metrics** | `outputs/metrics/zeroshot_31b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 76.2% | 100% | 0.466 |
| critical | 76.9% | 97.9% | 0.474 |
| applied | 65.7% | 100% | 0.516 |
| governance | 76.2% | 99.3% | 0.490 |
| **joint (all 4)** | **32.2%** | — | — |

Conceptual human code 1 → pred 0: **6** rows. Applied human code 1 → pred 2: **29** rows.

#### Round 2b · loosened prompt · 31B-it few-shot×10 · n=133 — job 6050891

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 00:42 ET |
| **Elapsed** | 45:42 |
| **Model** | `google/gemma-4-31B-it` |
| **Prompt** | Loosened rubric + 10 calibration exemplars (held out) |
| **Data** | `data/coding.csv`, n=133 (143 − 10 exemplars) |
| **Job** | Slurm `6050891`, PACE ICE H200 |
| **Preds** | `outputs/preds_fewshot10_31b_n143.csv` |
| **Metrics** | `outputs/metrics/fewshot10_31b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 60.9% | 100% | 0.421 |
| critical | 78.9% | 98.5% | 0.533 |
| applied | 66.9% | 100% | 0.576 |
| governance | 75.9% | 100% | 0.493 |
| **joint (all 4)** | **24.1%** | — | — |

Conceptual human code 1 → pred 0: **28** rows. Applied human code 1 → pred 2: **22** rows.

#### Round 2b conclusion (loosened prompt)

Only 31B zero-shot (6050890) is at or above about 65% exact on every dimension. Applied is the dimension that just clears that bar (65.7%). Joint exact is still 32.2%, because a call has to be right on all four scores at once.

Loosening conceptual (a 1 is any real AI capability, not only a mechanism) fixed the zero-shot conceptual collapse. Few-shot made conceptual worse on both sizes (56.4% and 60.9%) and cut joint exact (15.0% and 24.1%, against 28.7% and 32.2% zero-shot). The 10 exemplars still teach some sheet/guide conflicts, so few-shot is not currently helping.

Applied human code 1 predicted as 2 is still the main remaining miss (43, 40, 29, and 22 rows).

These scores measure agreement with the human codes in `data/coding.csv`. Where the written coding guide is stricter than the sheet (for example TR009 conceptual, TR163 critical), matching the sheet is not the same as following the guide.

### Sheet-aligned rerun — prompt told to match the human coding sheet (jobs 6052529–6052532; zero-shot n=143, few-shot n=133)

Jobs finished 2026-10-03, all exit 0: 6052529 (12B zero-shot, 36:44, ended 01:56 ET), 6052530 (12B few-shot×10, 36:21, ended 01:56 ET), 6052531 (31B zero-shot, 43:24, ended 02:03 ET), 6052532 (31B few-shot×10, 46:45, ended 02:06 ET). The human coding is in `data/coding.csv`. The cluster copies of `src/prompts.py` (01:18 ET) and `configs/fewshot_exemplars.json` (01:19 ET) are the files these jobs loaded. Slurm logs wrote the same `outputs/preds_*_n143.csv` names as Round 2b, and the file timestamps match these jobs, so the Round 2b CSVs were overwritten.

#### Sheet-aligned comparison — exact agreement (sheet-aligned prompt; zero-shot n=143, few-shot n=133)

| Job | Model | Prompt | n | Exact conceptual | Exact critical | Exact applied | Exact governance | Joint exact |
|-----|-------|--------|--:|-----------------:|---------------:|--------------:|-----------------:|------------:|
| **6052529** | **12B-it** | **zero-shot** | **143** | **81.1%** | **76.9%** | **73.4%** | **74.8%** | **42.7%** |
| 6052530 | 12B-it | few-shot×10 | 133 | 53.4% | 78.2% | 72.2% | 74.4% | 23.3% |
| 6052531 | 31B-it | zero-shot | 143 | 79.0% | 79.7% | 74.8% | 76.2% | 39.9% |
| 6052532 | 31B-it | few-shot×10 | 133 | 67.7% | 80.5% | 69.2% | 72.9% | 33.8% |

#### Sheet-aligned vs Round 2b — exact, QWK and confusion counts (n=143 zero-shot, n=133 few-shot)

Round 2b numbers are the historical writeup above. They were not recomputed. Arrows point from Round 2b to this rerun.

| Run | Joint exact | Conceptual exact / QWK | Applied exact / QWK | Governance exact / QWK | Conceptual 1→0 | Applied 1→2 |
|-----|-------------|------------------------|---------------------|------------------------|----------------:|------------:|
| 12B zero-shot | 28.7% → 42.7% | 78.3% / 0.494 → 81.1% / 0.545 | 59.4% / 0.462 → 73.4% / 0.553 | 76.9% / 0.603 → 74.8% / 0.462 | 4 → 2 | 43 → 6 |
| 12B few-shot×10 | 15.0% → 23.3% | 56.4% / 0.379 → 53.4% / 0.384 | 59.4% / 0.494 → 72.2% / 0.616 | 75.9% / 0.514 → 74.4% / 0.270 | 33 → 36 | 40 → 12 |
| 31B zero-shot | 32.2% → 39.9% | 76.2% / 0.466 → 79.0% / 0.471 | 65.7% / 0.516 → 74.8% / 0.571 | 76.2% / 0.490 → 76.2% / 0.403 | 6 → 2 | 29 → 4 |
| 31B few-shot×10 | 24.1% → 33.8% | 60.9% / 0.421 → 67.7% / 0.424 | 66.9% / 0.576 → 69.2% / 0.507 | 75.9% / 0.493 → 72.9% / 0.335 | 28 → 17 | 22 → 8 |

#### Sheet-aligned · 12B-it zero-shot · n=143 — job 6052529

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 01:56 ET |
| **Elapsed** | 36:44 |
| **Exit** | 0 |
| **Model** | `google/gemma-4-12B-it` |
| **Prompt** | Sheet-aligned rubric, zero-shot |
| **Data** | `data/coding.csv`, n=143 |
| **Job** | Slurm `6052529`, PACE ICE H200 |
| **Preds** | `outputs/preds_zeroshot_12b_n143.csv` |
| **Metrics** | `outputs/metrics/sheetalign_zeroshot_12b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 81.1% | 100% | 0.545 |
| critical | 76.9% | 98.6% | 0.509 |
| applied | 73.4% | 100% | 0.553 |
| governance | 74.8% | 99.3% | 0.462 |
| **joint (all 4)** | **42.7%** | — | — |

Conceptual human code 1 → pred 0: **2** rows. Applied human code 1 → pred 2: **6** rows.

#### Sheet-aligned · 12B-it few-shot×10 · n=133 — job 6052530

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 01:56 ET |
| **Elapsed** | 36:21 |
| **Exit** | 0 |
| **Model** | `google/gemma-4-12B-it` |
| **Prompt** | Sheet-aligned rubric + 10 calibration exemplars (held out) |
| **Data** | `data/coding.csv`, n=133 (143 − 10 exemplars) |
| **Job** | Slurm `6052530`, PACE ICE H200 |
| **Preds** | `outputs/preds_fewshot10_12b_n143.csv` |
| **Metrics** | `outputs/metrics/sheetalign_fewshot10_12b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 53.4% | 100% | 0.384 |
| critical | 78.2% | 99.2% | 0.510 |
| applied | 72.2% | 99.2% | 0.616 |
| governance | 74.4% | 97.7% | 0.270 |
| **joint (all 4)** | **23.3%** | — | — |

Conceptual human code 1 → pred 0: **36** rows. Applied human code 1 → pred 2: **12** rows.

#### Sheet-aligned · 31B-it zero-shot · n=143 — job 6052531

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 02:03 ET |
| **Elapsed** | 43:24 |
| **Exit** | 0 |
| **Model** | `google/gemma-4-31B-it` |
| **Prompt** | Sheet-aligned rubric, zero-shot |
| **Data** | `data/coding.csv`, n=143 |
| **Job** | Slurm `6052531`, PACE ICE H200 |
| **Preds** | `outputs/preds_zeroshot_31b_n143.csv` |
| **Metrics** | `outputs/metrics/sheetalign_zeroshot_31b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 79.0% | 100% | 0.471 |
| critical | 79.7% | 99.3% | 0.551 |
| applied | 74.8% | 100% | 0.571 |
| governance | 76.2% | 98.6% | 0.403 |
| **joint (all 4)** | **39.9%** | — | — |

Conceptual human code 1 → pred 0: **2** rows. Applied human code 1 → pred 2: **4** rows.

#### Sheet-aligned · 31B-it few-shot×10 · n=133 — job 6052532

| Field | Value |
|-------|-------|
| **Finished** | 2026-10-03 02:06 ET |
| **Elapsed** | 46:45 |
| **Exit** | 0 |
| **Model** | `google/gemma-4-31B-it` |
| **Prompt** | Sheet-aligned rubric + 10 calibration exemplars (held out) |
| **Data** | `data/coding.csv`, n=133 (143 − 10 exemplars) |
| **Job** | Slurm `6052532`, PACE ICE H200 |
| **Preds** | `outputs/preds_fewshot10_31b_n143.csv` |
| **Metrics** | `outputs/metrics/sheetalign_fewshot10_31b_n143.json` |

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 67.7% | 100% | 0.424 |
| critical | 80.5% | 99.2% | 0.558 |
| applied | 69.2% | 98.5% | 0.507 |
| governance | 72.9% | 98.5% | 0.335 |
| **joint (all 4)** | **33.8%** | — | — |

Conceptual human code 1 → pred 0: **17** rows. Applied human code 1 → pred 2: **8** rows.

#### Sheet-aligned conclusion

The human coding is in `data/coding.csv`. These scores are agreement with that sheet, not with a stricter written guide.

Joint exact rose on every run versus Round 2b: 12B zero-shot 28.7% → 42.7%, 12B few-shot 15.0% → 23.3%, 31B zero-shot 32.2% → 39.9%, 31B few-shot 24.1% → 33.8%. The best joint score is now 12B zero-shot (6052529, 42.7%), ahead of 31B zero-shot (39.9%).

The applied human code 1 → pred 2 miss dropped on every run (43 → 6, 40 → 12, 29 → 4, 22 → 8). Applied exact rose with that: 59.4% → 73.4% (12B zero), 59.4% → 72.2% (12B few), 65.7% → 74.8% (31B zero), 66.9% → 69.2% (31B few). Applied QWK rose on the first three of those and fell on 31B few-shot (0.576 → 0.507).

Zero-shot conceptual stayed high and moved up a little (12B 78.3% / 0.494 → 81.1% / 0.545; 31B 76.2% / 0.466 → 79.0% / 0.471). Conceptual human code 1 → pred 0 fell on both zero-shot runs (4 → 2 and 6 → 2). Few-shot conceptual is still the weak cell. 12B few-shot got slightly worse (56.4% → 53.4%; 1→0 33 → 36). 31B few-shot improved (60.9% → 67.7%; 1→0 28 → 17) but remains below its own zero-shot conceptual (79.0% vs 67.7%) and below its own zero-shot joint (39.9% vs 33.8%).

Three runs are at or above 65% exact on every dimension: 12B zero-shot (lowest 73.4% applied), 31B zero-shot (lowest 74.8% applied), and 31B few-shot (lowest 67.7% conceptual). 12B few-shot is not (conceptual 53.4%).

Governance did not improve. Exact stayed in the low-to-mid 70s (76.9% → 74.8%, 75.9% → 74.4%, 76.2% → 76.2%, 75.9% → 72.9%). Governance QWK fell on every run (0.603 → 0.462, 0.514 → 0.270, 0.490 → 0.403, 0.493 → 0.335). The 12B few-shot governance QWK of 0.270 is the low point.

Few-shot still trails zero-shot on joint exact for both sizes. Matching the sheet is still not the same as following the written coding guide where the two disagree.


## 5. Metrics glossary

Rough interpretation bands are conventions, not hard cut-offs. κ bands follow Landis & Koch, α bands follow Krippendorff, and ICC bands follow Koo & Li.

| Metric | Plain meaning | Rough bands |
|---|---|---|
| **Exact agreement** | Share of cases where the model's score equals the human score, shown as % (k/n). | No chance correction, so it looks high when most cases share one score. |
| **Adjacent agreement** | Share of cases where the model and human scores differ by at most 1. | On a 0–2 scale this is nearly always high. It only catches 0-vs-2 disagreements. |
| **Linear weighted κ** | Cohen's κ, which corrects agreement for chance, with partial credit that falls linearly with distance (off by 1 counts half as bad as off by 2). This is the advisor's primary measure. | <.20 slight, .21–.40 fair, .41–.60 moderate, .61–.80 substantial, >.80 almost perfect. .70 is the working bar in the advisor's note. |
| **Quadratic weighted κ (QWK)** | The same, but the penalty grows with the square of the distance, so off-by-one is penalised lightly. This is the "QWK" in the run logs. | Same bands as linear κ. |
| **Ordinal Krippendorff's α** | A chance-corrected reliability coefficient for ordered categories. Distances between categories depend on how often each score is used. | ≥.800 reliable, .667–.800 enough for tentative conclusions, <.667 unreliable. |
| **ICC(A,1)** | Intraclass correlation, two-way random, absolute agreement, single rater, on the four-dimension composite. It asks whether the two raters give the same composite value, not just the same ranking. | <.50 poor, .50–.75 moderate, .75–.90 good, >.90 excellent. |
| **Joint exact** | Share of cases where all four dimensions match exactly. This is the advisor's "Exact agreement" on the overall row. | Compounds across dimensions. Four dimensions near 75–80% each give roughly 30–45%. |

Why κ and α can be low when exact agreement looks high: the human codes are concentrated on one or two values. In `data/coding.csv` (n=143), conceptual is 3 / 102 / 38 at scores 0 / 1 / 2, critical is 101 / 36 / 6, applied is 11 / 85 / 47, and governance is 100 / 37 / 6. With that skew, a coder that mostly picks the common score gets high exact agreement but little credit after chance correction. The rare scores, such as governance 1 and 2, decide κ and α.

## 6. Conclusions and next steps

*This section was written for jobs 6052529–6052532 and Round 2b. For the 2026-10-19 experiments, including the new best run (prompt v3, 5-sample vote, job 6392418), see section 8.*

**Against the human benchmark (best run, sheet-aligned 12B zero-shot, n=143):**
- **Conceptual:** linear κ .526 vs .817, α .560 vs .848, exact 81.1% vs 90.5%. Below the humans. κ is held down partly because human conceptual 0 is very rare (3 of 143).
- **Critical:** .488 vs .700, α .526 vs .711, exact 76.9% vs 83.3%. This is the closest dimension, but it is still below .70.
- **Applied:** .492 vs .824, α .524 vs .830, exact 73.4% vs 90.5%. This is a large gap. Most remaining misses are human 2 scored as 1 (26 rows), now that the human 1 → model 2 miss is down to 6.
- **Governance:** .379 vs .705, α .408 vs .751, exact 74.8% vs 81.0%. This is the weakest dimension. The model misses many human 1s (25 rows scored 0), and governance QWK fell versus Round 2b on every run.
- **Composite:** ICC(A,1) .701 [.594–.783] vs .849 [.695–.942]. Mean absolute difference 0.191 vs 0.143. Joint exact 42.7% vs 61.9%.
- No model run reaches linear κ .70 on any dimension. The highest single value across all eight runs is .552 (sheet-aligned 12B few-shot, applied).

**Across runs:**
- **Few-shot hurts.** On both model sizes and both prompts, the 10 exemplars lower conceptual agreement sharply (sheet-aligned 12B conceptual linear κ .526 → .236) and lower joint exact. The current exemplar set should not be reused.
- **12B zero-shot vs 31B zero-shot:** 12B has the higher joint exact (42.7% vs 39.9%), mean linear κ (.472 vs .457) and composite ICC (.701 vs .656). 31B is slightly higher on critical (.500 vs .488) and applied (.515 vs .492) linear κ. The 31B model does not clearly beat 12B.
- **Sheet-aligned vs Round 2b:** sheet alignment raised per-dimension exact and linear κ on conceptual, critical and applied, mainly by fixing the applied 1 → 2 over-scoring. Governance got worse (12B zero-shot linear κ .491 → .379).

**Limits:**
- Different case sets: the human benchmark uses 42 cases, and the model evaluation uses 143 or 133.
- The model is compared with one set of human codes (the coding sheet). The human benchmark compares two coders with each other.
- The coding sheet and the written guide disagree in places, so matching the sheet is not the same as following the guide.
- The composite-row method is our own (see section 2), because the advisor's exact computation is not given.
- The bootstrap CIs cover case resampling only. They do not cover prompt or seed variation.

**Next steps:**
1. Error pass on the rows the best run still misses, starting with governance (human 1 → model 0) and applied (human 2 → model 1). Then tighten those two rules in the prompt.
2. Rebuild the few-shot set from cases where the sheet and the rule agree, or drop few-shot.
3. If possible, score the model on the same 42 cases the human coders overlapped on. That would give a like-for-like comparison with the benchmark.
4. Once agreement is acceptable to the advisor, start the CEO-gender join and the market-response analysis.

## 7. How to reproduce

From the repo root:

```bash
# Exact / adjacent / QWK / joint exact (existing script)
python -m src.validate --preds outputs/preds_zeroshot_12b_n143.csv

# Advisor-format agreement: linear and quadratic κ, ordinal Krippendorff's α, exact (k/n),
# composite row, ICC(A,1) with bootstrap CI, mean absolute difference.
# Needs: pip install krippendorff   (pingouin is optional, used only to cross-check ICC)
python -m src.agreement --preds outputs/preds_zeroshot_12b_n143.csv --codes data/coding.csv --tag sheetalign_zeroshot_12b
python -m src.agreement --preds outputs/round2b_loosened/preds_zeroshot_12b_n143.csv --tag round2b_zeroshot_12b
```

Options for `src.agreement`: `--n-boot 2000` and `--seed 20261019` are the defaults. The output JSON goes to `outputs/metrics/agreement_<tag>.json`. Rows with a missing, non-numeric, or out-of-range prediction on any dimension are dropped from all metrics and listed in the JSON (`n_dropped_invalid`, `dropped_uids`).

The numbers in this file were produced in a clean virtual environment (numpy 2.4.6, pandas 3.0.6, scikit-learn 1.9.1, krippendorff 0.9.0, pingouin 0.7.0). The Anaconda base environment on this Mac mixes NumPy 1.x and 2.x builds, so a separate venv is recommended:

```bash
python3 -m venv /tmp/aglit_venv && /tmp/aglit_venv/bin/pip install pandas numpy scipy scikit-learn krippendorff pingouin
/tmp/aglit_venv/bin/python -m src.agreement --preds <csv> --tag <tag>
```

## 8. Experiments of 2026-10-19: per-dimension prompts, voting, boundary few-shot, prompt v3

All seven runs use Gemma 4 12B-it on one PACE ICE H200 and are scored against the human codes in `data/coding.csv` with `src/agreement.py`. All finished with exit 0 (ended 02:52–03:34 ET, 2026-10-19). Every prediction is a valid 0/1/2, so 0 rows were dropped. The baseline is the sheet-aligned 12B zero-shot run (job 6052529). The boundary few-shot run holds out its 10 exemplars, so compare it with the baseline restricted to the same 133 calls.

**Modes.**
- **Per-dimension:** four prompts per call, each with one dimension's rubric only.
- **5-sample vote:** the same prompt sampled 5 times (temperature 0.7, top_p 0.95), then a per-dimension majority vote, with ties going to the lower score.
- **Boundary few-shot×10:** 10 exemplars chosen mainly from governance and critical boundary cases.
- **Prompt v3** (`--prompt-version v3`) changes the rubric only:
  - Governance: security, privacy, fraud, risk, compliance, access control, human review or oversight connected to AI counts toward governance. Passing words with no substance stay 0.
  - Critical: neutral prerequisites and "early days" remarks are 0.
  - Applied: AI across several functions, or a measured outcome, scale or integration, is 2.
  - Conceptual: an in-depth account of how a system works is 2.

### 8a. All runs at a glance

| Run | n | Linear κ conceptual | Linear κ critical | Linear κ applied | Linear κ governance | Mean of 4 linear κ | Overall-average ordinal α | Composite ICC(A,1) | Joint exact |
|---|--:|---:|---:|---:|---:|---:|---:|---:|---:|
| Baseline: sheet-aligned · 12B-it zero-shot · job 6052529 | 143 | .526 | .488 | .492 | .379 | .472 | .666 | .701 | 42.7% |
| Baseline restricted to the 133 non-exemplar calls | 133 | .534 | .500 | .479 | .423 | .484 | .679 | .709 | 44.4% |
| Sheet-aligned · 12B-it per-dimension · job 6392317 | 143 | .528 | .432 | .372 | .361 | .423 | .644 | .671 | 34.3% |
| Sheet-aligned · 12B-it 5-sample vote · job 6392318 | 143 | .495 | .488 | .504 | .392 | .470 | .662 | .712 | 42.0% |
| Sheet-aligned · 12B-it per-dimension + 5-sample vote · job 6392319 | 143 | .528 | .422 | .378 | .374 | .425 | .646 | .674 | 35.7% |
| Sheet-aligned · 12B-it boundary few-shot×10 · job 6392320 | 133 | .481 | .431 | .528 | .550 | .497 | .711 | .775 | 30.1% |
| Prompt v3 · 12B-it zero-shot · job 6392416 | 143 | .547 | .491 | .365 | .633 | .509 | .675 | .731 | 29.4% |
| Prompt v3 · 12B-it per-dimension · job 6392417 | 143 | .466 | .472 | .386 | .728 | .513 | .668 | .723 | 30.8% |
| **Prompt v3 · 12B-it 5-sample vote · job 6392418** | **143** | **.568** | **.542** | **.365** | **.633** | **.527** | **.683** | **.744** | **29.4%** |
| *Human vs human (Lee vs Elsie)* | *42* | *.817* | *.700* | *.824* | *.705* | *.762* | *.858* | *.849* | *61.9%* |

Best by mean of the four linear κ: **prompt v3 · 12B-it 5-sample vote (job 6392418)**, .527 against .472 for the baseline. Its overall-average ordinal α is .683 against .666 for the baseline. That is the highest of the 2026-10-19 n=143 runs, but below the Round 2b loosened-prompt zero-shot runs (.696 for 12B, .720 for 31B). Its joint exact is lower (29.4% against 42.7%).

**What the confusion counts show** (from the prediction files and `data/coding.csv`):
- **Prompt v3, governance:** human 1 scored 0 fell from 25 (baseline) to 15 (v3 zero-shot and v3 vote) and 10 (v3 per-dimension). Governance linear κ rose from .379 to .633, and to .728 per-dimension.
- **Prompt v3, applied:** human 1 scored 2 rose from 6 to 48 (v3 zero-shot and v3 vote) and 42 (v3 per-dimension). Applied linear κ fell from .492 to .365. This is why joint exact drops to about 30% on every v3 run. The v3 applied rule now over-scores 2.
- **Voting:** on the sheet-aligned prompt, voting left the scores almost unchanged (mean linear κ .470 against .472). On v3 it raised critical (.491 → .542) and conceptual (.547 → .568), and left applied and governance the same.
- **Per-dimension prompts:** these lowered critical and applied on the sheet-aligned prompt (critical 0 scored 1 rose from 15 to 23, and applied 2 scored 1 from 26 to 31). On v3, per-dimension gave the best governance (.728) but the lowest conceptual (.466).
- **Boundary few-shot:** on the same 133 calls, mean linear κ was .497 against .484 for the baseline. Governance (.550 against .423) and applied (.528 against .479) were higher. Conceptual (.481 against .534) and critical (.431 against .500) were lower, and joint exact fell from 44.4% to 30.1%.
- **Against the human benchmark:** no run reaches linear κ .70 on every dimension. The only value at or above .70 is v3 per-dimension governance (.728, human .705).

### 8b. Per-run tables

#### Sheet-aligned prompt · 12B-it per-dimension (4 prompts per call) · job 6392317 · n=143

Predictions: `outputs/preds_perdim_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_perdim_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .528 | .552 | .571 | 79.0% (113/143) |
| Critical | .432 | .472 | .454 | 72.0% (103/143) |
| Applied | .372 | .443 | .406 | 66.4% (95/143) |
| Governance | .361 | .407 | .371 | 74.8% (107/143) |
| Overall four-dimension average | .483 | .670 | .644 | 34.3% (49/143) |

Composite: ICC(A,1) = **.671** (95% bootstrap CI .564–.756). Interval α = .668. Mean absolute difference between model and human codes = 0.208 points on the 0–2 scale. Rows dropped as invalid: 0. 7 of 572 dimension calls returned unparseable JSON and default to 0 (TR012 governance, TR015 conceptual, TR027 governance, TR107 critical, TR111 applied, TR129 governance, TR170 critical).

#### Sheet-aligned prompt · 12B-it 5-sample vote · job 6392318 · n=143

Predictions: `outputs/preds_vote5_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_vote5_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .495 | .519 | .535 | 79.7% (114/143) |
| Critical | .488 | .509 | .526 | 76.9% (110/143) |
| Applied | .504 | .562 | .534 | 74.1% (106/143) |
| Governance | .392 | .474 | .421 | 75.5% (108/143) |
| Overall four-dimension average | .513 | .710 | .662 | 42.0% (60/143) |

Composite: ICC(A,1) = **.712** (95% bootstrap CI .610–.791). Interval α = .707. Mean absolute difference between model and human codes = 0.191 points on the 0–2 scale. Rows dropped as invalid: 0. Samples: `outputs/samples_vote5_zeroshot_12b_n143.jsonl` (715 samples, 2 unparseable: TR086, TR124; those calls were voted on 4 samples).

#### Sheet-aligned prompt · 12B-it per-dimension + 5-sample vote · job 6392319 · n=143

Predictions: `outputs/preds_perdim_vote5_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_perdim_vote5_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .528 | .552 | .571 | 79.0% (113/143) |
| Critical | .422 | .462 | .442 | 71.3% (102/143) |
| Applied | .378 | .444 | .408 | 67.1% (96/143) |
| Governance | .374 | .419 | .383 | 75.5% (108/143) |
| Overall four-dimension average | .494 | .673 | .646 | 35.7% (51/143) |

Composite: ICC(A,1) = **.674** (95% bootstrap CI .568–.760). Interval α = .671. Mean absolute difference between model and human codes = 0.203 points on the 0–2 scale. Rows dropped as invalid: 0. Samples: `outputs/samples_perdim_vote5_zeroshot_12b_n143.jsonl` (2,860 samples, 27 unparseable across 10 call-dimensions). TR170 critical failed on all 5 samples and defaults to 0.

#### Sheet-aligned prompt · 12B-it boundary few-shot×10 · job 6392320 · n=133

Predictions: `outputs/preds_fewshot_boundary10_12b_n133.csv` · JSON: `outputs/metrics/agreement_fewshot_boundary10_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .481 | .522 | .549 | 73.7% (98/133) |
| Critical | .431 | .460 | .466 | 73.7% (98/133) |
| Applied | .528 | .595 | .577 | 69.9% (93/133) |
| Governance | .550 | .642 | .549 | 81.2% (108/133) |
| Overall four-dimension average | .549 | .774 | .711 | 30.1% (40/133) |

Composite: ICC(A,1) = **.775** (95% bootstrap CI .682–.840). Interval α = .774. Mean absolute difference between model and human codes = 0.195 points on the 0–2 scale. Rows dropped as invalid: 0. Exemplars (held out): TR170, TR034, TR005, TR006, TR125, TR107, TR113, TR244, TR083, TR024 (`configs/fewshot_exemplars_boundary.json`). Compare with the same-133 baseline below.

#### Prompt v3 · 12B-it zero-shot · job 6392416 · n=143

Predictions: `outputs/preds_fix3_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_fix3_zeroshot_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .547 | .565 | .582 | 81.8% (117/143) |
| Critical | .491 | .499 | .533 | 78.3% (112/143) |
| Applied | .365 | .480 | .373 | 55.9% (80/143) |
| Governance | .633 | .708 | .658 | 82.5% (118/143) |
| Overall four-dimension average | .505 | .730 | .675 | 29.4% (42/143) |

Composite: ICC(A,1) = **.731** (95% bootstrap CI .630–.803). Interval α = .731. Mean absolute difference between model and human codes = 0.210 points on the 0–2 scale. Rows dropped as invalid: 0.

#### Prompt v3 · 12B-it per-dimension · job 6392417 · n=143

Predictions: `outputs/preds_fix3_perdim_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_fix3_perdim_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .466 | .454 | .490 | 74.8% (107/143) |
| Critical | .472 | .518 | .533 | 74.8% (107/143) |
| Applied | .386 | .468 | .404 | 58.7% (84/143) |
| Governance | .728 | .778 | .723 | 86.7% (124/143) |
| Overall four-dimension average | .495 | .721 | .668 | 30.8% (44/143) |

Composite: ICC(A,1) = **.723** (95% bootstrap CI .628–.795). Interval α = .720. Mean absolute difference between model and human codes = 0.226 points on the 0–2 scale. Rows dropped as invalid: 0. 6 of 572 dimension calls returned unparseable JSON and default to 0 (TR027 governance, TR043 conceptual, TR046 applied, TR104 critical, TR106 conceptual, TR188 conceptual).

#### Prompt v3 · 12B-it 5-sample vote · job 6392418 · n=143

Predictions: `outputs/preds_fix3_vote5_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_fix3_vote5_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .568 | .586 | .603 | 82.5% (118/143) |
| Critical | .542 | .550 | .569 | 80.4% (115/143) |
| Applied | .365 | .480 | .373 | 55.9% (80/143) |
| Governance | .633 | .708 | .658 | 82.5% (118/143) |
| Overall four-dimension average | .516 | .743 | .683 | 29.4% (42/143) |

Composite: ICC(A,1) = **.744** (95% bootstrap CI .643–.816). Interval α = .743. Mean absolute difference between model and human codes = 0.206 points on the 0–2 scale. Rows dropped as invalid: 0. Samples: `outputs/samples_fix3_vote5_zeroshot_12b_n143.jsonl` (715 samples, 0 unparseable). The 5 samples agreed on every dimension for most calls (132–136 of 143 per dimension), so this run differs from v3 zero-shot on only a few calls.

#### Baseline restricted to the 133 non-exemplar calls (for the boundary few-shot run)

Predictions: `outputs/analysis/baseline_zeroshot_12b_excl_boundary_n133.csv` (job 6052529 minus the 10 boundary exemplars) · JSON: `outputs/metrics/agreement_sheetalign_zeroshot_12b_same133.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .534 | .554 | .571 | 81.2% (108/133) |
| Critical | .500 | .513 | .531 | 78.2% (104/133) |
| Applied | .479 | .544 | .513 | 72.2% (96/133) |
| Governance | .423 | .524 | .457 | 76.7% (102/133) |
| Overall four-dimension average | .525 | .708 | .679 | 44.4% (59/133) |

Composite: ICC(A,1) = **.709** (95% bootstrap CI .599–.792). Interval α = .705. Mean absolute difference between model and human codes = 0.188 points on the 0–2 scale. Rows dropped as invalid: 0.

**Files.** Slurm logs are in `slurm/<job>.out` and `slurm/<job>.err`. The code is in `src/infer_gemma.py` (`--prompt-mode perdim`, `--num-samples`, `--prompt-version v3`), with `scripts/run_code_gemma.sbatch` (MODE, PROMPT_VERSION), `scripts/queue_improvements.sh` and `scripts/queue_fix3.sh`. The miss analysis is in `outputs/analysis/misses_sheetalign_12b_zeroshot.md`.
