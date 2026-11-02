# AI Literacy Coding — Exhaustive Results

**What this file is.** The full record behind `RESULTS.md`: every run (Round 2b loosened prompt and sheet-aligned prompt; Gemma 4 12B-it and 31B-it; zero-shot and few-shot×10), per-run agreement tables, exact / adjacent / QWK tables, confusion counts, job metadata, the composite-metric method, notes, conclusions, and how to reproduce. Section 8 adds the 2026-10-19 experiments (per-dimension prompts, 5-sample voting, boundary few-shot, prompts v3 and v4) on the 143 calls; the best of those was prompt v4, Gemma 4 12B-it zero-shot (job 6408582). Section 9 covers the new 200-call set compiled 2026-10-30 (`data/coding_n200.csv`): 19 runs and 8 ensembles. Section 10 adds prompt v5 and DEV/TEST splits on both coding sets. `RESULTS.md` shows the best method on the 200 calls, prompt v5 · Gemma 4 31B-it · zero-shot (job 6714845), on the held-out TEST half, with all 200 calls alongside. It also states that v4 12B zero-shot remains best on the 143 calls.

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
8. Experiments of 2026-10-19 (per-dimension, voting, boundary few-shot, prompts v3 and v4)
9. New data: 200 calls compiled 2026-10-30 (all prompts × models × modes, ensembles, score distributions)
10. Prompt v5 and DEV/TEST splits (both coding sets)

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

Best run by mean linear κ: **prompt v4, Gemma 4 12B-it zero-shot, job 6408582, n=143** (section 8). Earlier bests (sheet-aligned 12B zero-shot, job 6052529, and prompt v3 5-sample vote, job 6392418) are in 2c and section 8.

| Dimension | Human–human linear κ | Model linear κ | Human–human ordinal α | Model ordinal α | Human–human exact | Model exact |
|---|---:|---:|---:|---:|---:|---:|
| Conceptual | .817 | .495 | .848 | .535 | 90.5% (38/42) | 79.7% (114/143) |
| Critical | .700 | .505 | .711 | .540 | 83.3% (35/42) | 78.3% (112/143) |
| Applied | .824 | .520 | .830 | .571 | 90.5% (38/42) | 73.4% (105/143) |
| Governance | .705 | .591 | .751 | .613 | 81.0% (34/42) | 80.4% (115/143) |
| Overall four-dimension average | .738 | .573 | .858 | .711 | 61.9% (26/42) | 42.7% (61/143) |
| Composite ICC(A,1) [95% CI] | .849 [.695–.942] | .761 [.669–.831] | | | | |
| Composite mean absolute difference | 0.143 | 0.177 | | | | |

Every model linear κ is below the human–human value.
- **Governance:** the gap is smallest here (.591 vs .705).
- **Critical:** .505 vs .700.
- **Applied:** .520 vs .824.
- **Conceptual:** the gap is largest here (.495 vs .817).
- **Exact agreement:** below the human coders on every dimension, from 0.6 points (governance) to 17.1 points (applied). Joint exact is 42.7% vs 61.9%.

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
| Prompt v3 · 12B-it 5-sample vote · job 6392418 | 143 | .568 | .542 | .365 | .633 | .527 | .744 | 29.4% |
| **Prompt v4 · 12B-it zero-shot · job 6408582** | **143** | **.495** | **.505** | **.520** | **.591** | **.528** | **.761** | **42.7%** |
| Prompt v4 · 12B-it 5-sample vote · job 6408585 | 143 | .517 | .501 | .468 | .541 | .507 | .764 | 39.9% |
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

*This section was written for jobs 6052529–6052532 and Round 2b. For the 2026-10-19 experiments, including the new best run (prompt v4, zero-shot, job 6408582), see section 8.*

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

## 8. Experiments of 2026-10-19: per-dimension prompts, voting, boundary few-shot, prompts v3 and v4

All nine runs use Gemma 4 12B-it on one PACE ICE H200 and are scored against the human codes in `data/coding.csv` with `src/agreement.py`. All finished with exit 0. The first seven ended 02:52–03:34 ET on 2026-10-19. The two prompt v4 runs ended 23:59 ET on 2026-10-19 and 04:10 ET on 2026-10-20. Every prediction is a valid 0/1/2, so 0 rows were dropped. The baseline is the sheet-aligned 12B zero-shot run (job 6052529). The boundary few-shot run holds out its 10 exemplars, so compare it with the baseline restricted to the same 133 calls.

**Modes.**
- **Per-dimension:** four prompts per call, each with one dimension's rubric only.
- **5-sample vote:** the same prompt sampled 5 times (temperature 0.7, top_p 0.95), then a per-dimension majority vote, with ties going to the lower score.
- **Boundary few-shot×10:** 10 exemplars chosen mainly from governance and critical boundary cases.
- **Prompt v3** (`--prompt-version v3`) changes the rubric only:
  - Governance: security, privacy, fraud, risk, compliance, access control, human review or oversight connected to AI counts toward governance. Passing words with no substance stay 0.
  - Critical: neutral prerequisites and "early days" remarks are 0.
  - Applied: AI across several functions, or a measured outcome, scale or integration, is 2.
  - Conceptual: an in-depth account of how a system works is 2.
- **Prompt v4** (`--prompt-version v4`) is identical to v3 except for the applied dimension, which uses the sheet-aligned (baseline) applied wording again. A stated use is 1. Score 2 requires depth, scale, integration or a measured outcome. Between 1 and 2, assign 1.

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
| Prompt v3 · 12B-it 5-sample vote · job 6392418 | 143 | .568 | .542 | .365 | .633 | .527 | .683 | .744 | 29.4% |
| **Prompt v4 · 12B-it zero-shot · job 6408582** | **143** | **.495** | **.505** | **.520** | **.591** | **.528** | **.711** | **.761** | **42.7%** |
| Prompt v4 · 12B-it 5-sample vote · job 6408585 | 143 | .517 | .501 | .468 | .541 | .507 | .713 | .764 | 39.9% |
| *Human vs human (Lee vs Elsie)* | *42* | *.817* | *.700* | *.824* | *.705* | *.762* | *.858* | *.849* | *61.9%* |

Best by mean of the four linear κ: **prompt v4 · 12B-it zero-shot (job 6408582)**, .528 against .472 for the baseline. It is level with prompt v3 · 5-sample vote (.527; the unrounded difference is .0007). On the tiebreak measures it is clearly ahead of v3 vote:
- Overall-average ordinal α .711 against .683 (baseline .666).
- Composite ICC(A,1) .761 against .744 (baseline .701).
- Joint exact 42.7% against 29.4% (baseline 42.7%).

Prompt v4 keeps most of v3's governance gain (linear κ .591, against .633 for v3 zero-shot and .379 at baseline) and removes v3's applied over-scoring (human applied 1 scored 2: 7 calls, against 48 under v3 and 6 at baseline). Voting did not help v4. Mean linear κ was .507 against .528 for zero-shot, and joint exact 39.9% against 42.7%. The 5 samples agreed on 127–137 of 143 calls per dimension, and the vote changed the final score on 1–4 calls per dimension.

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

#### Prompt v4 · 12B-it zero-shot · job 6408582 · n=143

Predictions: `outputs/preds_fix4_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_fix4_zeroshot_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .495 | .519 | .535 | 79.7% (114/143) |
| Critical | .505 | .526 | .540 | 78.3% (112/143) |
| Applied | .520 | .587 | .571 | 73.4% (105/143) |
| Governance | .591 | .674 | .613 | 80.4% (115/143) |
| Overall four-dimension average | .573 | .760 | .711 | 42.7% (61/143) |

Composite: ICC(A,1) = **.761** (95% bootstrap CI .669–.831). Interval α = .759. Mean absolute difference between model and human codes = 0.177 points on the 0–2 scale. Rows dropped as invalid: 0. No unparseable output.

#### Prompt v4 · 12B-it 5-sample vote · job 6408585 · n=143

Predictions: `outputs/preds_fix4_vote5_zeroshot_12b_n143.csv` · JSON: `outputs/metrics/agreement_fix4_vote5_12b.json`

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .517 | .539 | .557 | 80.4% (115/143) |
| Critical | .501 | .515 | .525 | 78.3% (112/143) |
| Applied | .468 | .543 | .522 | 70.6% (101/143) |
| Governance | .541 | .629 | .576 | 78.3% (112/143) |
| Overall four-dimension average | .570 | .762 | .713 | 39.9% (57/143) |

Composite: ICC(A,1) = **.764** (95% bootstrap CI .669–.834). Interval α = .761. Mean absolute difference between model and human codes = 0.177 points on the 0–2 scale. Rows dropped as invalid: 0. Samples: `outputs/samples_fix4_vote5_zeroshot_12b_n143.jsonl` (715 samples, 10 unparseable: TR044 ×4, TR115 ×3, TR082, TR100, TR134). Each of those calls was voted on its remaining 1–4 parsed samples.

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

**Files.** Slurm logs are in `slurm/<job>.out` and `slurm/<job>.err`. The code is in `src/infer_gemma.py` (`--prompt-mode perdim`, `--num-samples`, `--prompt-version v3`), with `scripts/run_code_gemma.sbatch` (MODE, PROMPT_VERSION), `scripts/queue_improvements.sh`, `scripts/queue_fix3.sh` and `scripts/queue_fix4.sh`. The miss analysis is in `outputs/analysis/misses_sheetalign_12b_zeroshot.md`.

## 9. New data: 200 calls compiled 2026-10-30 (`data/coding_n200.csv`)

### 9a. Data

- Source: `data/Training_Compiled_10-30-2026(Coding).csv` from the advisor, exported unchanged to `data/coding_n200.csv` with the column names used by `data/coding.csv` (`<dim> (0-2)`, `overall`). Strategic is not in the file.
- 200 calls, IDs `S2-0001`… (157) and `S3-0001`…`S3-0056` (43). Every row has its own AI-related sentences (no empty text) and valid 0/1/2 codes; `overall` equals the mean of the four codes on every row. One row (S3-0009) lists 4 sentences but its text has 5 bullets.
- **No overlap with the 143-call set.** No call text and no single sentence appears in both files. Four call titles match (TR007/S3-0045 SAP, TR008/S2-0027 Udemy, TR064/S2-0058 Data#3, TR129/S2-0145 Bitdeer), but the sentences, speakers and codes differ. So these runs test the prompts on 200 calls they were never tuned on; they are not a recode of the old calls.
- The calls are shorter: median 4 AI sentences (mean 7.2) against 8 (11.5) in the 143-call set.
- Human code distribution (% at 0 / 1 / 2), 143-call set → 200-call set:

| Dimension | 143 calls | 200 calls |
|---|---|---|
| Conceptual | 2 / 71 / 27 | 10 / 50 / 39 |
| Critical | 71 / 25 / 4 | 74 / 24 / 2 |
| Applied | 8 / 59 / 33 | 15 / 48 / 36 |
| Governance | 70 / 26 / 4 | 86 / 12 / 2 |

### 9b. Runs

Gemma 4 12B-it and 31B-it on one PACE ICE H200 each. Prompts: sheet-aligned (baseline), v3 and v4 (section 8; prompt text unchanged). Modes: zero-shot; vote5 (5 samples at temperature 0.7, top_p 0.95, per-dimension majority, ties to the lower score); few-shot×10 with the boundary exemplars in `configs/fewshot_exemplars_boundary.json` (all from the 143-call set, so all 200 calls are scored), placed after the selected prompt's system message; per-dimension (four prompts per call). All 19 jobs finished with exit 0, used the real model (no dry run), returned 200 rows with valid 0/1/2 scores, and 0 rows were dropped in scoring.

| Job | Prompt | Model | Mode | Elapsed | Ended (ET, 2026-10-31) | Predictions (`outputs/`) |
|---|---|---|---|---:|---:|---|
| 6690852 | v4 | 12B | zero-shot | 44:30 | 01:44 | `preds_fix4_zeroshot_12b_n200.csv` |
| 6690853 | v4 | 31B | zero-shot | 45:24 | 01:57 | `preds_fix4_zeroshot_31b_n200.csv` |
| 6690854 | sheet-aligned | 12B | zero-shot | 42:50 | 02:42 | `preds_zeroshot_12b_n200.csv` |
| 6690855 | v3 | 12B | zero-shot | 45:49 | 03:04 | `preds_fix3_zeroshot_12b_n200.csv` |
| 6690856 | v4 | 12B | vote5 | 47:58 | 03:09 | `preds_fix4_vote5_zeroshot_12b_n200.csv` |
| 6690868 | sheet-aligned | 31B | zero-shot | 44:33 | 03:10 | `preds_zeroshot_31b_n200.csv` |
| 6690869 | v3 | 31B | zero-shot | 48:16 | 03:30 | `preds_fix3_zeroshot_31b_n200.csv` |
| 6690870 | sheet-aligned | 12B | vote5 | 45:51 | 03:31 | `preds_vote5_zeroshot_12b_n200.csv` |
| 6690871 | v3 | 12B | vote5 | 50:54 | 04:23 | `preds_fix3_vote5_zeroshot_12b_n200.csv` |
| 6690872 | sheet-aligned | 31B | vote5 | 1:05:25 | 05:28 | `preds_vote5_zeroshot_31b_n200.csv` |
| 6690873 | v3 | 31B | vote5 | 1:04:03 | 05:33 | `preds_fix3_vote5_zeroshot_31b_n200.csv` |
| 6690874 | v4 | 31B | vote5 | 1:02:54 | 05:32 | `preds_fix4_vote5_zeroshot_31b_n200.csv` |
| 6690875 | sheet-aligned | 12B | few-shot×10 | 1:02:39 | 04:57 | `preds_fewshot_boundary10_12b_n200.csv` |
| 6690876 | sheet-aligned | 31B | few-shot×10 | 1:02:33 | 06:33 | `preds_fewshot_boundary10_31b_n200.csv` |
| 6690877 | v3 | 12B | few-shot×10 | 49:25 | 04:54 | `preds_fix3_fewshot_boundary10_12b_n200.csv` |
| 6690878 | v3 | 31B | few-shot×10 | 1:02:47 | 06:35 | `preds_fix3_fewshot_boundary10_31b_n200.csv` |
| 6690879 | v4 | 12B | few-shot×10 | 49:19 | 05:31 | `preds_fix4_fewshot_boundary10_12b_n200.csv` |
| 6690880 | v4 | 31B | few-shot×10 | 1:02:09 | 06:35 | `preds_fix4_fewshot_boundary10_31b_n200.csv` |
| 6690881 | v4 | 12B | per-dimension | 1:15:29 | 06:55 | `preds_fix4_perdim_zeroshot_12b_n200.csv` |

Parse failures (the score defaults to 0): v4 12B zero-shot 1 call (S3-0045); v3 12B zero-shot 3 calls (S2-0133, S2-0148, S3-0013); v4 12B per-dimension 5 single-dimension prompts (S2-0028, S2-0086, S2-0143, S3-0009, S3-0016). Vote5: 6 of 1,000 samples unparsed for v4 12B and 5 of 1,000 for v3 12B, others 0; every call kept at least one parsed sample.

**Ensembles** (`scripts/ensemble.py`, built and scored by `scripts/score_n200.py`). Per-dimension majority across the member runs; the first member breaks ties (with three members a tie means 0/1/2).
- ens_v4_12b31b_sheet12b: v4 12B zero + v4 31B zero + sheet-aligned 12B zero.
- ens_v4_12b31b_v3_12b: v4 12B zero + v4 31B zero + v3 12B zero.
- ens_v4_trio: v4 12B zero + v4 31B zero + v4 12B vote5.
- ens_xprompt_12b / ens_xprompt_31b: the three prompts, zero-shot, at 12B / 31B (31B ties go to v4 31B).
- ens_zs6: majority of all six zero-shot runs; a tie goes to v4 12B if its score is among the tied ones, else the lower score.
- ens_zs6_mean: mean of the six zero-shot runs, rounded; an exact .5 goes toward v4 12B.
- ens_best3_old: chosen before seeing any n=200 result, as the best runs on the 143-call set by mean linear κ: v4 12B zero (.528), v3 12B vote5 (.527) and the best 31B run there, sheet-aligned 31B zero (.457). v3 and v4 were never run at 31B on the 143 calls.

### 9c. All runs at a glance (sorted by mean of the four linear κ)

Overall = four-dimension average; joint exact = all four dimensions match; MAD = mean absolute difference of the overall average.

| Run | Prompt | Model | Mode | Con lin κ | Cri lin κ | App lin κ | Gov lin κ | Mean lin κ | Overall lin κ | Overall quad κ | Overall ord α | ICC(A,1) [95% CI] | MAD | Joint exact | n |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| v3_fs10_31b | v3 | 31B | few-shot (10 boundary) | .271 | .329 | .531 | .547 | .419 | .439 | .653 | .647 | .654 [.573–.722] | 0.255 | 23.5% | 200 |
| v4_fs10_12b | v4 | 12B | few-shot (10 boundary) | .307 | .381 | .547 | .442 | .419 | .452 | .661 | .675 | .662 [.580–.730] | 0.251 | 24.0% | 200 |
| v4_fs10_31b | v4 | 31B | few-shot (10 boundary) | .283 | .342 | .507 | .534 | .417 | .411 | .626 | .630 | .628 [.549–.695] | 0.263 | 25.0% | 200 |
| v3_fs10_12b | v3 | 12B | few-shot (10 boundary) | .283 | .373 | .541 | .468 | .416 | .449 | .653 | .659 | .654 [.567–.727] | 0.256 | 22.5% | 200 |
| v3_zs_12b | v3 | 12B | zero-shot | .208 | .354 | .544 | .542 | .412 | .452 | .650 | .661 | .651 [.565–.722] | 0.244 | 25.0% | 200 |
| v3_vote5_12b | v3 | 12B | vote5 | .226 | .354 | .532 | .529 | .411 | .460 | .666 | .676 | .667 [.585–.734] | 0.237 | 24.5% | 200 |
| ens_v4_12b31b_v3_12b | ensemble | mixed | majority: v4 12B zero + v4 31B zero + v3 12B zero | .217 | .354 | .484 | .542 | .399 | .417 | .605 | .625 | .606 [.514–.685] | 0.253 | 27.5% | 200 |
| ens_best3_old | ensemble | mixed | majority of the best 3 on old n=143 data (v4 12B zero, v3 12B vote5, sheet-aligned 31B zero) | .217 | .354 | .484 | .542 | .399 | .417 | .605 | .625 | .606 [.514–.685] | 0.253 | 27.5% | 200 |
| ens_xprompt_12b | ensemble | mixed | majority across prompts at 12B (v4/v3/sheet-aligned zero) | .217 | .354 | .477 | .542 | .398 | .420 | .600 | .621 | .601 [.507–.684] | 0.249 | 28.0% | 200 |
| v4_zs_12b | v4 | 12B | zero-shot | .214 | .354 | .469 | .518 | .389 | .417 | .598 | .614 | .599 [.505–.680] | 0.253 | 27.5% | 200 |
| v4_perdim_12b | v4 | 12B | per-dimension | .302 | .337 | .421 | .467 | .382 | .446 | .640 | .657 | .641 [.559–.711] | 0.245 | 27.5% | 200 |
| ens_v4_trio | ensemble | mixed | majority: v4 12B zero + v4 31B zero + v4 12B vote5 | .211 | .332 | .475 | .505 | .381 | .419 | .589 | .608 | .591 [.495–.673] | 0.253 | 28.0% | 200 |
| v4_vote5_12b | v4 | 12B | vote5 | .224 | .332 | .469 | .493 | .380 | .417 | .589 | .607 | .590 [.494–.672] | 0.253 | 28.0% | 200 |
| ens_zs6_mean | ensemble | mixed | mean of all six zero-shot runs, rounded; exact .5 toward v4 12B | .192 | .356 | .489 | .478 | .379 | .400 | .577 | .610 | .578 [.487–.661] | 0.256 | 27.5% | 200 |
| ens_zs6 | ensemble | mixed | majority of all six zero-shot runs (3 prompts x 2 models); tie -> v4 12B if tied, else lower | .192 | .356 | .489 | .478 | .379 | .400 | .577 | .610 | .578 [.487–.661] | 0.256 | 27.5% | 200 |
| v3_zs_31b | v3 | 31B | zero-shot | .208 | .329 | .543 | .401 | .370 | .426 | .624 | .659 | .625 [.542–.698] | 0.249 | 23.0% | 200 |
| sheet_fs10_12b | sheet-aligned | 12B | few-shot (10 boundary) | .290 | .355 | .562 | .271 | .369 | .396 | .603 | .609 | .605 [.514–.683] | 0.274 | 23.0% | 200 |
| v3_vote5_31b | v3 | 31B | vote5 | .211 | .329 | .528 | .401 | .367 | .420 | .621 | .653 | .622 [.538–.695] | 0.251 | 22.0% | 200 |
| ens_v4_12b31b_sheet12b | ensemble | mixed | majority: v4 12B zero + v4 31B zero + sheet-aligned 12B zero | .189 | .356 | .440 | .478 | .366 | .391 | .563 | .596 | .564 [.471–.647] | 0.259 | 27.5% | 200 |
| v4_zs_31b | v4 | 31B | zero-shot | .186 | .329 | .458 | .486 | .365 | .359 | .542 | .589 | .544 [.457–.624] | 0.271 | 26.5% | 200 |
| v4_vote5_31b | v4 | 31B | vote5 | .183 | .319 | .468 | .476 | .361 | .369 | .552 | .595 | .553 [.463–.632] | 0.269 | 27.0% | 200 |
| ens_xprompt_31b | ensemble | mixed | majority across prompts at 31B (v4/v3/sheet-aligned zero); tie -> v4 31B | .186 | .329 | .474 | .401 | .347 | .357 | .533 | .574 | .535 [.444–.619] | 0.273 | 26.5% | 200 |
| sheet_fs10_31b | sheet-aligned | 31B | few-shot (10 boundary) | .249 | .327 | .551 | .210 | .334 | .383 | .573 | .599 | .574 [.490–.648] | 0.270 | 25.5% | 200 |
| sheet_vote5_12b | sheet-aligned | 12B | vote5 | .195 | .318 | .423 | .226 | .290 | .341 | .489 | .498 | .490 [.379–.586] | 0.278 | 27.5% | 200 |
| sheet_zs_12b | sheet-aligned | 12B | zero-shot | .182 | .327 | .423 | .226 | .289 | .343 | .493 | .508 | .494 [.384–.591] | 0.275 | 27.5% | 200 |
| sheet_vote5_31b | sheet-aligned | 31B | vote5 | .193 | .357 | .466 | .142 | .289 | .317 | .491 | .528 | .492 [.401–.575] | 0.289 | 25.5% | 200 |
| sheet_zs_31b | sheet-aligned | 31B | zero-shot | .186 | .357 | .466 | .142 | .288 | .319 | .492 | .534 | .494 [.403–.578] | 0.287 | 25.5% | 200 |
| *Human vs human (Lee vs Elsie, 42 older calls)* | | | | *.817* | *.700* | *.824* | *.705* | *.762* | *.738* | *.846* | *.858* | *.849 [.695–.942]* | *0.143* | *61.9%* | *42* |

Best by mean of the four linear κ: **v4 · 12B · few-shot×10** and **v3 · 31B · few-shot×10** are level (.4193 and .4194). On the context measures v4 12B few-shot is ahead: overall-average ordinal α .675 against .647, ICC(A,1) .662 against .654, joint exact 24.0% against 23.5%. It is also the smaller model, so `RESULTS.md` shows v4 12B few-shot×10.

### 9d. Score distributions, model vs human (% of calls at 0 / 1 / 2)

| Run | Conceptual | Critical | Applied | Governance |
|---|---|---|---|---|
| human codes | 10 / 50 / 39 | 74 / 24 / 2 | 15 / 48 / 36 | 86 / 12 / 2 |
| v4_zs_12b | 14 / 76 / 10 | 86 / 12 / 2 | 22 / 60 / 18 | 84 / 15 / 0 |
| v4_zs_31b | 14 / 76 / 10 | 89 / 10 / 0 | 24 / 62 / 15 | 89 / 11 / 0 |
| v3_zs_12b | 14 / 76 / 10 | 86 / 12 / 2 | 24 / 36 / 40 | 86 / 14 / 0 |
| v3_zs_31b | 14 / 76 / 10 | 89 / 10 / 0 | 26 / 32 / 42 | 91 / 8 / 0 |
| sheet_zs_12b | 13 / 78 / 9 | 84 / 15 / 0 | 17 / 68 / 16 | 93 / 6 / 0 |
| sheet_zs_31b | 14 / 76 / 10 | 88 / 12 / 0 | 24 / 61 / 16 | 96 / 4 / 0 |
| v4_vote5_12b | 14 / 76 / 10 | 86 / 12 / 1 | 22 / 60 / 18 | 85 / 14 / 0 |
| v4_vote5_31b | 14 / 76 / 10 | 88 / 11 / 0 | 24 / 61 / 15 | 89 / 10 / 0 |
| v3_vote5_12b | 12 / 77 / 11 | 86 / 12 / 2 | 24 / 36 / 41 | 85 / 14 / 0 |
| v3_vote5_31b | 13 / 76 / 10 | 89 / 10 / 0 | 26 / 31 / 42 | 91 / 8 / 0 |
| sheet_vote5_12b | 14 / 78 / 9 | 84 / 16 / 0 | 17 / 68 / 16 | 93 / 6 / 0 |
| sheet_vote5_31b | 14 / 77 / 9 | 88 / 12 / 0 | 24 / 61 / 16 | 96 / 4 / 0 |
| v4_fs10_12b | 17 / 64 / 19 | 78 / 19 / 2 | 29 / 42 / 28 | 88 / 11 / 1 |
| v4_fs10_31b | 16 / 68 / 16 | 88 / 10 / 1 | 30 / 46 / 24 | 89 / 10 / 2 |
| v3_fs10_12b | 18 / 64 / 18 | 78 / 20 / 2 | 31 / 34 / 36 | 88 / 12 / 1 |
| v3_fs10_31b | 16 / 68 / 15 | 89 / 10 / 0 | 34 / 33 / 33 | 90 / 9 / 2 |
| sheet_fs10_12b | 18 / 64 / 18 | 81 / 17 / 2 | 30 / 42 / 29 | 93 / 6 / 0 |
| sheet_fs10_31b | 16 / 68 / 16 | 86 / 12 / 2 | 28 / 46 / 26 | 94 / 5 / 0 |
| v4_perdim_12b | 14 / 70 / 16 | 82 / 15 / 3 | 28 / 60 / 12 | 79 / 20 / 0 |
| ens_v4_12b31b_sheet12b | 14 / 77 / 10 | 86 / 14 / 0 | 21 / 63 / 16 | 88 / 12 / 0 |
| ens_v4_12b31b_v3_12b | 13 / 77 / 10 | 86 / 12 / 2 | 23 / 58 / 19 | 86 / 14 / 0 |
| ens_v4_trio | 14 / 76 / 10 | 86 / 12 / 1 | 23 / 60 / 18 | 86 / 14 / 0 |
| ens_xprompt_12b | 13 / 77 / 10 | 86 / 12 / 2 | 20 / 62 / 18 | 86 / 14 / 0 |
| ens_xprompt_31b | 14 / 76 / 10 | 89 / 10 / 0 | 24 / 60 / 16 | 91 / 8 / 0 |
| ens_zs6 | 13 / 78 / 10 | 86 / 14 / 0 | 22 / 58 / 19 | 88 / 12 / 0 |
| ens_zs6_mean | 13 / 78 / 10 | 86 / 14 / 0 | 22 / 58 / 19 | 88 / 12 / 0 |
| ens_best3_old | 13 / 77 / 10 | 86 / 12 / 2 | 23 / 58 / 19 | 86 / 14 / 0 |

### 9e. Notes

- **Agreement is lower than on the 143 calls for every configuration.** The best mean linear κ is .419 here, against .528 for v4 12B zero-shot on the 143 calls. The same run (v4 12B zero-shot) scores .389 here. Overall-average ordinal α is at most .676 here (v3 12B vote5) against .711, and joint exact is 22–28% against 42.7%.
- **Conceptual is the main drop** (linear κ .18–.31, against about .50 on the 143 calls). Human codes put 39% of calls at conceptual 2; zero-shot and vote5 runs give 2 to only 9–11% and few-shot runs to 15–19%. For v4 12B zero-shot, 61 of 78 human conceptual 2s are scored 1; with few-shot×10 it is 45 of 78. Human conceptual 0 (10%) is also matched poorly: v4 12B gets 7 (zero-shot) and 8 (few-shot) of 21.
- **Applied is under-scored by v4 and the sheet-aligned prompt** (2 on 15–18% of calls against 36% for the humans; v4 12B zero-shot scores 41 of 73 human 2s as 1). v3, whose applied rule over-scored 2 on the 143 calls, is closer to the new distribution (33–42% at 2), and few-shot moves v4 to 24–28%. Applied linear κ is .42–.56.
- **Governance is not over-scored on this set.** Humans give governance ≥1 to 14% of calls; v4 and v3 give 8–20% and the sheet-aligned prompt 4–7% (under). Governance linear κ is highest with v3 zero-shot 12B (.542) and v3 few-shot 31B (.547); the sheet-aligned prompt is lowest (.14–.27) because it misses most human 1s.
- **Critical is under-scored:** humans give ≥1 to 26% of calls; zero-shot and vote5 runs give 10–16% and few-shot 12B runs 19–22%. Critical linear κ is .32–.38 for every run.
- **Few-shot×10 helps more on this set than on the 143 calls.** With the sheet-aligned prompt at 12B, mean linear κ rises .289 → .369 here, against .484 → .497 on the same 133 calls before. Four of the five best runs are few-shot, mainly through conceptual (+.06 to +.11 over the matching zero-shot run).
- **Voting and ensembles add little.** The six zero-shot runs agree closely: each ensemble changes only 7–21 of 800 scores relative to v4 12B zero-shot. ens_v4_12b31b_v3_12b and ens_best3_old produce identical predictions, as do ens_zs6 and ens_zs6_mean. The best ensemble (.399) is below the best single runs (.419). vote5 is within ±.01 of zero-shot for every prompt and model.
- **31B is not better than 12B.** Mean linear κ is lower at 31B for every prompt and mode, except v3 few-shot, where the two are level (.419 against .416). 31B few-shot does raise governance for v3 and v4 (.547 and .534 against .468 and .442).
- **No run reaches the human benchmark** on any dimension in linear κ. Few-shot v4 12B governance exact agreement (86.0%) is above the human figure (81.0%), but this mostly reflects the 86% base rate of governance 0.

### 9f. Per-run tables

#### v4_zs_12b — v4, 12B, zero-shot

`outputs/preds_fix4_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .214 | .347 | .291 | 51.0% (102/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .469 | .580 | .560 | 62.5% (125/200) |
| Governance | .518 | .550 | .573 | 87.0% (174/200) |
| Overall four-dimension average | .417 | .598 | .614 | 27.5% (55/200) |

ICC(A,1) = .599 (95% bootstrap CI .505–.680); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.557.

#### v4_zs_31b — v4, 31B, zero-shot

`outputs/preds_fix4_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .186 | .325 | .267 | 49.0% (98/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .458 | .584 | .553 | 61.0% (122/200) |
| Governance | .486 | .516 | .532 | 88.0% (176/200) |
| Overall four-dimension average | .359 | .542 | .589 | 26.5% (53/200) |

ICC(A,1) = .544 (95% bootstrap CI .457–.624); mean |human − model| = 0.271; composite mean human 0.738 vs model 0.524.

#### v3_zs_12b — v3, 12B, zero-shot

`outputs/preds_fix3_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .208 | .329 | .273 | 51.0% (102/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .544 | .649 | .655 | 65.0% (130/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .452 | .650 | .661 | 25.0% (50/200) |

ICC(A,1) = .651 (95% bootstrap CI .565–.722); mean |human − model| = 0.244; composite mean human 0.738 vs model 0.606.

#### v3_zs_31b — v3, 31B, zero-shot

`outputs/preds_fix3_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .208 | .342 | .291 | 50.5% (101/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .543 | .662 | .646 | 63.5% (127/200) |
| Governance | .401 | .462 | .454 | 86.5% (173/200) |
| Overall four-dimension average | .426 | .624 | .659 | 23.0% (46/200) |

ICC(A,1) = .625 (95% bootstrap CI .542–.698); mean |human − model| = 0.249; composite mean human 0.738 vs model 0.584.

#### sheet_zs_12b — sheet-aligned, 12B, zero-shot

`outputs/preds_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .182 | .316 | .255 | 49.5% (99/200) |
| Critical | .327 | .360 | .353 | 76.5% (153/200) |
| Applied | .423 | .539 | .517 | 61.0% (122/200) |
| Governance | .226 | .284 | .253 | 84.0% (168/200) |
| Overall four-dimension average | .343 | .493 | .508 | 27.5% (55/200) |

ICC(A,1) = .494 (95% bootstrap CI .384–.591); mean |human − model| = 0.275; composite mean human 0.738 vs model 0.545.

#### sheet_zs_31b — sheet-aligned, 31B, zero-shot

`outputs/preds_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .186 | .325 | .267 | 49.0% (98/200) |
| Critical | .357 | .389 | .379 | 78.5% (157/200) |
| Applied | .466 | .590 | .561 | 61.5% (123/200) |
| Governance | .142 | .184 | .143 | 84.5% (169/200) |
| Overall four-dimension average | .319 | .492 | .534 | 25.5% (51/200) |

ICC(A,1) = .494 (95% bootstrap CI .403–.578); mean |human − model| = 0.287; composite mean human 0.738 vs model 0.512.

#### v4_vote5_12b — v4, 12B, vote5

`outputs/preds_fix4_vote5_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .224 | .360 | .302 | 51.0% (102/200) |
| Critical | .332 | .377 | .363 | 77.0% (154/200) |
| Applied | .469 | .580 | .560 | 62.5% (125/200) |
| Governance | .493 | .530 | .548 | 86.5% (173/200) |
| Overall four-dimension average | .417 | .589 | .607 | 28.0% (56/200) |

ICC(A,1) = .590 (95% bootstrap CI .494–.672); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.552.

#### v4_vote5_31b — v4, 31B, vote5

`outputs/preds_fix4_vote5_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .183 | .325 | .267 | 48.5% (97/200) |
| Critical | .319 | .357 | .335 | 77.5% (155/200) |
| Applied | .468 | .592 | .561 | 61.5% (123/200) |
| Governance | .476 | .521 | .534 | 87.5% (175/200) |
| Overall four-dimension average | .369 | .552 | .595 | 27.0% (54/200) |

ICC(A,1) = .553 (95% bootstrap CI .463–.632); mean |human − model| = 0.269; composite mean human 0.738 vs model 0.524.

#### v3_vote5_12b — v3, 12B, vote5

`outputs/preds_fix3_vote5_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .226 | .350 | .299 | 52.5% (105/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .532 | .650 | .651 | 63.5% (127/200) |
| Governance | .529 | .561 | .587 | 87.5% (175/200) |
| Overall four-dimension average | .460 | .666 | .676 | 24.5% (49/200) |

ICC(A,1) = .667 (95% bootstrap CI .585–.734); mean |human − model| = 0.237; composite mean human 0.738 vs model 0.618.

#### v3_vote5_31b — v3, 31B, vote5

`outputs/preds_fix3_vote5_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .211 | .342 | .291 | 51.0% (102/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .528 | .652 | .635 | 62.0% (124/200) |
| Governance | .401 | .462 | .454 | 86.5% (173/200) |
| Overall four-dimension average | .420 | .621 | .653 | 22.0% (44/200) |

ICC(A,1) = .622 (95% bootstrap CI .538–.695); mean |human − model| = 0.251; composite mean human 0.738 vs model 0.586.

#### sheet_vote5_12b — sheet-aligned, 12B, vote5

`outputs/preds_vote5_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .195 | .329 | .267 | 50.0% (100/200) |
| Critical | .318 | .351 | .344 | 76.0% (152/200) |
| Applied | .423 | .527 | .505 | 61.5% (123/200) |
| Governance | .226 | .284 | .253 | 84.0% (168/200) |
| Overall four-dimension average | .341 | .489 | .498 | 27.5% (55/200) |

ICC(A,1) = .490 (95% bootstrap CI .379–.586); mean |human − model| = 0.278; composite mean human 0.738 vs model 0.545.

#### sheet_vote5_31b — sheet-aligned, 31B, vote5

`outputs/preds_vote5_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .193 | .330 | .271 | 49.5% (99/200) |
| Critical | .357 | .389 | .379 | 78.5% (157/200) |
| Applied | .466 | .590 | .561 | 61.5% (123/200) |
| Governance | .142 | .184 | .143 | 84.5% (169/200) |
| Overall four-dimension average | .317 | .491 | .528 | 25.5% (51/200) |

ICC(A,1) = .492 (95% bootstrap CI .401–.575); mean |human − model| = 0.289; composite mean human 0.738 vs model 0.511.

#### v4_fs10_12b — v4, 12B, few-shot (10 boundary)

`outputs/preds_fix4_fewshot_boundary10_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .307 | .425 | .407 | 54.5% (109/200) |
| Critical | .381 | .437 | .422 | 75.5% (151/200) |
| Applied | .547 | .634 | .628 | 66.0% (132/200) |
| Governance | .442 | .503 | .468 | 86.0% (172/200) |
| Overall four-dimension average | .452 | .661 | .675 | 24.0% (48/200) |

ICC(A,1) = .662 (95% bootstrap CI .580–.730); mean |human − model| = 0.251; composite mean human 0.738 vs model 0.596.

#### v4_fs10_31b — v4, 31B, few-shot (10 boundary)

`outputs/preds_fix4_fewshot_boundary10_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .283 | .397 | .370 | 54.0% (108/200) |
| Critical | .342 | .413 | .376 | 77.5% (155/200) |
| Applied | .507 | .594 | .581 | 63.5% (127/200) |
| Governance | .534 | .592 | .540 | 88.5% (177/200) |
| Overall four-dimension average | .411 | .626 | .630 | 25.0% (50/200) |

ICC(A,1) = .628 (95% bootstrap CI .549–.695); mean |human − model| = 0.263; composite mean human 0.738 vs model 0.547.

#### v3_fs10_12b — v3, 12B, few-shot (10 boundary)

`outputs/preds_fix3_fewshot_boundary10_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .283 | .398 | .374 | 53.0% (106/200) |
| Critical | .373 | .429 | .413 | 75.0% (150/200) |
| Applied | .541 | .630 | .631 | 64.5% (129/200) |
| Governance | .468 | .524 | .497 | 86.5% (173/200) |
| Overall four-dimension average | .449 | .653 | .659 | 22.5% (45/200) |

ICC(A,1) = .654 (95% bootstrap CI .567–.727); mean |human − model| = 0.256; composite mean human 0.738 vs model 0.606.

#### v3_fs10_31b — v3, 31B, few-shot (10 boundary)

`outputs/preds_fix3_fewshot_boundary10_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .271 | .377 | .347 | 53.5% (107/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .531 | .617 | .619 | 63.5% (127/200) |
| Governance | .547 | .604 | .554 | 89.0% (178/200) |
| Overall four-dimension average | .439 | .653 | .647 | 23.5% (47/200) |

ICC(A,1) = .654 (95% bootstrap CI .573–.722); mean |human − model| = 0.255; composite mean human 0.738 vs model 0.552.

#### sheet_fs10_12b — sheet-aligned, 12B, few-shot (10 boundary)

`outputs/preds_fewshot_boundary10_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .290 | .402 | .378 | 53.5% (107/200) |
| Critical | .355 | .409 | .385 | 75.5% (151/200) |
| Applied | .562 | .637 | .634 | 67.5% (135/200) |
| Governance | .271 | .359 | .310 | 84.5% (169/200) |
| Overall four-dimension average | .396 | .603 | .609 | 23.0% (46/200) |

ICC(A,1) = .605 (95% bootstrap CI .514–.683); mean |human − model| = 0.274; composite mean human 0.738 vs model 0.569.

#### sheet_fs10_31b — sheet-aligned, 31B, few-shot (10 boundary)

`outputs/preds_fewshot_boundary10_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .249 | .368 | .342 | 52.0% (104/200) |
| Critical | .327 | .383 | .366 | 76.5% (153/200) |
| Applied | .551 | .632 | .623 | 67.0% (134/200) |
| Governance | .210 | .275 | .232 | 84.5% (169/200) |
| Overall four-dimension average | .383 | .573 | .599 | 25.5% (51/200) |

ICC(A,1) = .574 (95% bootstrap CI .490–.648); mean |human − model| = 0.270; composite mean human 0.738 vs model 0.547.

#### v4_perdim_12b — v4, 12B, per-dimension

`outputs/preds_fix4_perdim_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .302 | .428 | .400 | 55.5% (111/200) |
| Critical | .337 | .413 | .381 | 74.5% (149/200) |
| Applied | .421 | .521 | .480 | 59.0% (118/200) |
| Governance | .467 | .527 | .515 | 83.0% (166/200) |
| Overall four-dimension average | .446 | .640 | .657 | 27.5% (55/200) |

ICC(A,1) = .641 (95% bootstrap CI .559–.711); mean |human − model| = 0.245; composite mean human 0.738 vs model 0.573.

#### ens_v4_12b31b_sheet12b — ensemble, mixed, majority: v4 12B zero + v4 31B zero + sheet-aligned 12B zero

`outputs/preds_ens_v4_12b31b_sheet12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .189 | .325 | .267 | 49.5% (99/200) |
| Critical | .356 | .386 | .381 | 78.0% (156/200) |
| Applied | .440 | .564 | .541 | 60.5% (121/200) |
| Governance | .478 | .520 | .535 | 87.0% (174/200) |
| Overall four-dimension average | .391 | .563 | .596 | 27.5% (55/200) |

ICC(A,1) = .564 (95% bootstrap CI .471–.647); mean |human − model| = 0.259; composite mean human 0.738 vs model 0.546.

#### ens_v4_12b31b_v3_12b — ensemble, mixed, majority: v4 12B zero + v4 31B zero + v3 12B zero

`outputs/preds_ens_v4_12b31b_v3_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .217 | .346 | .291 | 51.5% (103/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .484 | .596 | .577 | 63.0% (126/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .417 | .605 | .625 | 27.5% (55/200) |

ICC(A,1) = .606 (95% bootstrap CI .514–.685); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.557.

#### ens_v4_trio — ensemble, mixed, majority: v4 12B zero + v4 31B zero + v4 12B vote5

`outputs/preds_ens_v4_trio_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .211 | .347 | .291 | 50.5% (101/200) |
| Critical | .332 | .377 | .363 | 77.0% (154/200) |
| Applied | .475 | .587 | .566 | 62.5% (125/200) |
| Governance | .505 | .540 | .561 | 87.0% (174/200) |
| Overall four-dimension average | .419 | .589 | .608 | 28.0% (56/200) |

ICC(A,1) = .591 (95% bootstrap CI .495–.673); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.550.

#### ens_xprompt_12b — ensemble, mixed, majority across prompts at 12B (v4/v3/sheet-aligned zero)

`outputs/preds_ens_xprompt_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .217 | .346 | .291 | 51.5% (103/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .477 | .583 | .565 | 63.5% (127/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .420 | .600 | .621 | 28.0% (56/200) |

ICC(A,1) = .601 (95% bootstrap CI .507–.684); mean |human − model| = 0.249; composite mean human 0.738 vs model 0.561.

#### ens_xprompt_31b — ensemble, mixed, majority across prompts at 31B (v4/v3/sheet-aligned zero); tie -> v4 31B

`outputs/preds_ens_xprompt_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .186 | .325 | .267 | 49.0% (98/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .474 | .597 | .569 | 62.0% (124/200) |
| Governance | .401 | .462 | .454 | 86.5% (173/200) |
| Overall four-dimension average | .357 | .533 | .574 | 26.5% (53/200) |

ICC(A,1) = .535 (95% bootstrap CI .444–.619); mean |human − model| = 0.273; composite mean human 0.738 vs model 0.522.

#### ens_zs6 — ensemble, mixed, majority of all six zero-shot runs (3 prompts x 2 models); tie -> v4 12B if tied, else lower

`outputs/preds_ens_zs6_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .192 | .324 | .267 | 50.0% (100/200) |
| Critical | .356 | .386 | .381 | 78.0% (156/200) |
| Applied | .489 | .608 | .590 | 63.0% (126/200) |
| Governance | .478 | .520 | .535 | 87.0% (174/200) |
| Overall four-dimension average | .400 | .577 | .610 | 27.5% (55/200) |

ICC(A,1) = .578 (95% bootstrap CI .487–.661); mean |human − model| = 0.256; composite mean human 0.738 vs model 0.551.

#### ens_zs6_mean — ensemble, mixed, mean of all six zero-shot runs, rounded; exact .5 toward v4 12B

`outputs/preds_ens_zs6_mean_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .192 | .324 | .267 | 50.0% (100/200) |
| Critical | .356 | .386 | .381 | 78.0% (156/200) |
| Applied | .489 | .608 | .590 | 63.0% (126/200) |
| Governance | .478 | .520 | .535 | 87.0% (174/200) |
| Overall four-dimension average | .400 | .577 | .610 | 27.5% (55/200) |

ICC(A,1) = .578 (95% bootstrap CI .487–.661); mean |human − model| = 0.256; composite mean human 0.738 vs model 0.551.

#### ens_best3_old — ensemble, mixed, majority of the best 3 on old n=143 data (v4 12B zero, v3 12B vote5, sheet-aligned 31B zero)

`outputs/preds_ens_best3_old_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .217 | .346 | .291 | 51.5% (103/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .484 | .596 | .577 | 63.0% (126/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .417 | .605 | .625 | 27.5% (55/200) |

ICC(A,1) = .606 (95% bootstrap CI .514–.685); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.557.

### 9g. How to reproduce

```bash
# on PACE, from the project root
bash scripts/queue_n200.sh          # v4 zero 12B/31B, sheet-aligned zero 12B, v3 zero 12B, v4 vote5 12B
bash scripts/queue_n200_matrix.sh   # the other 14 runs
# locally, after copying outputs/preds_*_n200.csv back
python scripts/score_n200.py        # agreement JSONs, ensembles, outputs/analysis/n200_comparison.md/.csv, n200_distributions.csv
```

## 10. Prompt v5 and DEV/TEST splits (runs of 2026-10-31)

### 10a. Method

- **Splits.** Each coding set is split into DEV and TEST with seed 20261031, stratified on conceptual × applied × (critical or governance ≥ 1):
  - 200-call set: 100 DEV / 100 TEST (`data/split_n200.csv`);
  - 143-call set: 70 DEV / 73 TEST (`data/split_n143.csv`).
  Prompt v5 and its examples were written from DEV only (`outputs/analysis/misses_n200_dev.md`). TEST is the headline.
- **Prompt v5** (`--prompt-version v5`). Changes from v4 are summarised in `docs/analysis/prompt_v5_changes.md`:
  - base rates from the pooled DEV split;
  - no "between 1 and 2, assign 1" default;
  - conceptual 2 for specific AI content developed across several statements;
  - applied 1 for supplying AI demand; applied 2 for two or more uses each with what the AI does, a measured outcome, a worked path or deployment at scale;
  - wider critical-1 triggers (AI-enabled threats, disruption risk, human judgment kept);
  - governance 1 for AI products whose purpose is security, safety, fraud prevention or compliance.
- **DEV examples.** `configs/fewshot_exemplars_n200dev.json` holds 10 DEV calls from the 200-call set. They are excluded from scoring on the 200-call set, so for every run on that set DEV is 90 calls and ALL is 190; TEST is unaffected. None of the examples is in the 143-call set.
- **Ensemble.** Per-dimension majority of v5 12B zero-shot, v5 31B zero-shot and v5 12B few-shot (DEV examples); ties go to v5 12B zero-shot.
- **Runs.** Nine jobs, 6714844–6714852, all exit 0, ending 20:09–22:36 ET on 2026-10-31. Each used the stated model (12B or 31B), the real model (no dry run) and valid 0/1/2 scores. Row counts: 200 for the 200-call set (190 for few-shot), 143 for the 143-call set.
- **Parse failures** (score defaults to 0): v5 12B zero-shot on the 200-call set, 4 calls (S2-0079, S2-0084, S2-0105, S3-0054); v5 12B zero-shot on the 143-call set, 1 call (TR081); v5 vote5, 7 of 1,000 samples unparsed. All others 0.
- **Scoring.** `scripts/score_splits.py` (`outputs/analysis/splits_comparison.md/.csv`). The sheet-aligned boundary few-shot baseline on the 143-call set holds out its own 10 examples, which are TR calls, so its TEST is 68 calls and DEV 65.

### 10b. Results by split

#### 200-call set (`data/coding_n200.csv`) · TEST

| Run | n | Lin κ C | Lin κ Cr | Lin κ A | Lin κ G | Mean lin κ | α C | α Cr | α A | α G | Overall-average α | ICC(A,1) | Joint exact |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| v5 · 12B · zero-shot | 100 | .387 | .396 | .542 | .476 | .450 | .527 | .423 | .675 | .504 | .733 | .706 | 27.0% |
| v5 · 31B · zero-shot | 100 | .476 | .444 | .563 | .470 | .488 | .612 | .491 | .665 | .497 | .771 | .759 | 34.0% |
| v5 · 12B · vote5 | 100 | .400 | .416 | .559 | .535 | .477 | .525 | .443 | .685 | .564 | .754 | .732 | 29.0% |
| v5 · 12B · few-shot (DEV examples) | 100 | .520 | .380 | .548 | .374 | .455 | .657 | .402 | .696 | .396 | .749 | .731 | 29.0% |
| v5 · 31B · few-shot (DEV examples) | 100 | .468 | .451 | .481 | .507 | .477 | .615 | .494 | .606 | .459 | .724 | .730 | 26.0% |
| v4 · 12B · few-shot (DEV examples) | 100 | .346 | .398 | .551 | .441 | .434 | .483 | .416 | .686 | .467 | .686 | .647 | 25.0% |
| Ensemble: v5 12B zero + v5 31B zero + v5 12B few-shot | 100 | .454 | .341 | .586 | .441 | .456 | .598 | .364 | .709 | .467 | .734 | .717 | 32.0% |
| *Baseline:* v3 · 12B · vote5 | 100 | .238 | .276 | .541 | .561 | .404 | .326 | .273 | .672 | .590 | .700 | .658 | 22.0% |
| *Baseline:* v4 · 12B · few-shot (boundary examples) | 100 | .315 | .311 | .529 | .414 | .392 | .453 | .325 | .625 | .440 | .684 | .628 | 22.0% |
| *Reference:* v4 · 12B · zero-shot | 100 | .219 | .276 | .450 | .535 | .370 | .324 | .273 | .565 | .562 | .634 | .587 | 22.0% |

#### 200-call set (`data/coding_n200.csv`) · DEV

| Run | n | Lin κ C | Lin κ Cr | Lin κ A | Lin κ G | Mean lin κ | α C | α Cr | α A | α G | Overall-average α | ICC(A,1) | Joint exact |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| v5 · 12B · zero-shot | 90 | .373 | .503 | .522 | .437 | .459 | .450 | .528 | .604 | .497 | .678 | .733 | 30.0% |
| v5 · 31B · zero-shot | 90 | .428 | .378 | .642 | .474 | .481 | .504 | .434 | .717 | .519 | .728 | .742 | 33.3% |
| v5 · 12B · vote5 | 90 | .382 | .503 | .566 | .437 | .472 | .451 | .528 | .661 | .497 | .715 | .756 | 32.2% |
| v5 · 12B · few-shot (DEV examples) | 90 | .331 | .562 | .631 | .292 | .454 | .462 | .593 | .715 | .358 | .704 | .730 | 28.9% |
| v5 · 31B · few-shot (DEV examples) | 90 | .327 | .386 | .564 | .453 | .433 | .476 | .461 | .635 | .536 | .702 | .740 | 23.3% |
| v4 · 12B · few-shot (DEV examples) | 90 | .288 | .448 | .621 | .292 | .412 | .414 | .511 | .720 | .358 | .700 | .712 | 27.8% |
| Ensemble: v5 12B zero + v5 31B zero + v5 12B few-shot | 90 | .397 | .503 | .635 | .428 | .491 | .482 | .528 | .711 | .495 | .707 | .746 | 33.3% |
| *Baseline:* v3 · 12B · vote5 | 90 | .197 | .411 | .523 | .460 | .398 | .267 | .447 | .627 | .525 | .641 | .676 | 26.7% |
| *Baseline:* v4 · 12B · few-shot (boundary examples) | 90 | .288 | .396 | .565 | .347 | .399 | .362 | .470 | .625 | .405 | .652 | .680 | 23.3% |
| *Reference:* v4 · 12B · zero-shot | 90 | .191 | .411 | .456 | .460 | .380 | .249 | .447 | .527 | .525 | .569 | .599 | 31.1% |

#### 200-call set (`data/coding_n200.csv`) · ALL

| Run | n | Lin κ C | Lin κ Cr | Lin κ A | Lin κ G | Mean lin κ | α C | α Cr | α A | α G | Overall-average α | ICC(A,1) | Joint exact |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| v5 · 12B · zero-shot | 190 | .380 | .448 | .533 | .455 | .454 | .490 | .472 | .642 | .501 | .709 | .718 | 28.4% |
| v5 · 31B · zero-shot | 190 | .454 | .413 | .600 | .472 | .485 | .562 | .463 | .689 | .508 | .751 | .749 | 33.7% |
| v5 · 12B · vote5 | 190 | .391 | .458 | .562 | .483 | .474 | .491 | .483 | .673 | .529 | .736 | .742 | 30.5% |
| v5 · 12B · few-shot (DEV examples) | 190 | .432 | .469 | .587 | .331 | .455 | .567 | .493 | .703 | .375 | .726 | .730 | 28.9% |
| v5 · 31B · few-shot (DEV examples) | 190 | .401 | .420 | .519 | .479 | .455 | .549 | .477 | .618 | .500 | .713 | .734 | 24.7% |
| v4 · 12B · few-shot (DEV examples) | 190 | .320 | .423 | .584 | .363 | .423 | .451 | .460 | .701 | .411 | .693 | .678 | 26.3% |
| Ensemble: v5 12B zero + v5 31B zero + v5 12B few-shot | 190 | .427 | .420 | .609 | .435 | .473 | .544 | .441 | .709 | .481 | .722 | .730 | 32.6% |
| *Baseline:* v3 · 12B · vote5 | 190 | .219 | .344 | .532 | .510 | .401 | .297 | .357 | .650 | .557 | .674 | .666 | 24.2% |
| *Baseline:* v4 · 12B · few-shot (boundary examples) | 190 | .303 | .356 | .546 | .379 | .396 | .409 | .397 | .624 | .421 | .671 | .654 | 22.6% |
| *Reference:* v4 · 12B · zero-shot | 190 | .207 | .344 | .453 | .497 | .375 | .289 | .357 | .546 | .543 | .604 | .592 | 26.3% |

#### 143-call set (`data/coding.csv`) · TEST

| Run | n | Lin κ C | Lin κ Cr | Lin κ A | Lin κ G | Mean lin κ | α C | α Cr | α A | α G | Overall-average α | ICC(A,1) | Joint exact |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| v5 · 12B · zero-shot | 73 | .541 | .412 | .236 | .531 | .430 | .564 | .440 | .242 | .596 | .651 | .648 | 31.5% |
| v5 · 31B · zero-shot | 73 | .394 | .503 | .293 | .442 | .408 | .386 | .536 | .305 | .473 | .677 | .691 | 28.8% |
| v5 · 12B · few-shot (DEV examples) | 73 | .413 | .412 | .341 | .456 | .406 | .450 | .423 | .294 | .517 | .649 | .661 | 21.9% |
| Ensemble: v5 12B zero + v5 31B zero + v5 12B few-shot | 73 | .483 | .503 | .244 | .476 | .427 | .476 | .536 | .234 | .536 | .657 | .671 | 30.1% |
| *Baseline:* v4 · 12B · zero-shot | 73 | .387 | .326 | .551 | .506 | .442 | .426 | .370 | .581 | .535 | .663 | .682 | 42.5% |
| *Baseline:* sheet-aligned · 12B · few-shot (boundary examples; exemplars held out) | 68 | .474 | .298 | .491 | .410 | .418 | .554 | .323 | .501 | .413 | .700 | .713 | 29.4% |
| *Reference:* v3 · 12B · vote5 | 73 | .495 | .387 | .331 | .622 | .459 | .530 | .413 | .296 | .657 | .659 | .677 | 31.5% |
| *Reference:* v4 · 12B · vote5 | 73 | .432 | .314 | .483 | .482 | .428 | .475 | .338 | .524 | .510 | .676 | .697 | 38.4% |

#### 143-call set (`data/coding.csv`) · DEV

| Run | n | Lin κ C | Lin κ Cr | Lin κ A | Lin κ G | Mean lin κ | α C | α Cr | α A | α G | Overall-average α | ICC(A,1) | Joint exact |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| v5 · 12B · zero-shot | 70 | .520 | .572 | .283 | .621 | .499 | .547 | .628 | .247 | .646 | .629 | .735 | 21.4% |
| v5 · 31B · zero-shot | 70 | .493 | .564 | .302 | .572 | .483 | .498 | .619 | .322 | .676 | .663 | .726 | 25.7% |
| v5 · 12B · few-shot (DEV examples) | 70 | .373 | .635 | .356 | .679 | .511 | .414 | .663 | .348 | .712 | .683 | .764 | 18.6% |
| Ensemble: v5 12B zero + v5 31B zero + v5 12B few-shot | 70 | .440 | .539 | .349 | .664 | .498 | .451 | .593 | .346 | .690 | .675 | .751 | 22.9% |
| *Baseline:* v4 · 12B · zero-shot | 70 | .596 | .620 | .481 | .675 | .593 | .627 | .648 | .551 | .697 | .750 | .824 | 42.9% |
| *Baseline:* sheet-aligned · 12B · few-shot (boundary examples; exemplars held out) | 65 | .489 | .527 | .565 | .666 | .562 | .544 | .578 | .654 | .681 | .706 | .823 | 30.8% |
| *Reference:* v3 · 12B · vote5 | 70 | .635 | .642 | .398 | .641 | .579 | .667 | .673 | .452 | .657 | .698 | .792 | 27.1% |
| *Reference:* v4 · 12B · vote5 | 70 | .596 | .620 | .448 | .600 | .566 | .627 | .648 | .515 | .650 | .743 | .819 | 41.4% |

#### 143-call set (`data/coding.csv`) · ALL

| Run | n | Lin κ C | Lin κ Cr | Lin κ A | Lin κ G | Mean lin κ | α C | α Cr | α A | α G | Overall-average α | ICC(A,1) | Joint exact |
|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|
| v5 · 12B · zero-shot | 143 | .531 | .507 | .259 | .576 | .468 | .555 | .546 | .242 | .621 | .643 | .694 | 26.6% |
| v5 · 31B · zero-shot | 143 | .444 | .539 | .298 | .505 | .447 | .441 | .580 | .312 | .568 | .673 | .709 | 27.3% |
| v5 · 12B · few-shot (DEV examples) | 143 | .393 | .543 | .349 | .568 | .463 | .431 | .555 | .320 | .611 | .673 | .716 | 20.3% |
| Ensemble: v5 12B zero + v5 31B zero + v5 12B few-shot | 143 | .462 | .526 | .295 | .568 | .463 | .462 | .567 | .287 | .609 | .670 | .713 | 26.6% |
| *Baseline:* v4 · 12B · zero-shot | 143 | .495 | .505 | .520 | .591 | .528 | .535 | .540 | .571 | .613 | .711 | .761 | 42.7% |
| *Baseline:* sheet-aligned · 12B · few-shot (boundary examples; exemplars held out) | 133 | .481 | .431 | .528 | .550 | .497 | .549 | .466 | .577 | .549 | .711 | .775 | 30.1% |
| *Reference:* v3 · 12B · vote5 | 143 | .568 | .542 | .365 | .633 | .527 | .603 | .569 | .373 | .658 | .683 | .744 | 29.4% |
| *Reference:* v4 · 12B · vote5 | 143 | .517 | .501 | .468 | .541 | .507 | .557 | .525 | .522 | .576 | .713 | .764 | 39.9% |

### 10c. Findings

- **200-call set: v5 is clearly better on TEST.**
  - The best run is v5 31B zero-shot: overall-average α .771, mean linear κ .488, ICC .759, joint exact 34.0%. Baselines: v3 12B vote5 α .700, κ .404, joint 22.0%; v4 12B few-shot α .684, κ .392.
  - Every v5 run (α .724–.771) beats both baselines on α, mean κ, ICC and joint exact.
  - Conceptual gains most (linear κ .39–.52 against .24 and .32).
  - Critical rises to .38–.45 (against .28 and .31). Applied is level (.48–.56 against .54 and .53).
- **200-call set, where v5 is worse:**
  - Governance: v3 12B vote5 has linear κ .561 / α .590. v5 is lower on every run: 31B zero-shot .470 / .497, vote5 .535 / .564, 12B few-shot .374 / .396.
  - Applied: v5 31B few-shot is .481, against .541 for v3 vote5.
- **200-call set, DEV vs TEST (overfitting check):** TEST is not below DEV. v5 31B zero-shot has overall α .728 on DEV and .771 on TEST; v5 12B zero-shot .678 and .733. The gains carry over to calls not used to write v5.
- **DEV examples alone.** v4 12B few-shot with the new DEV examples gets TEST α .686 and κ .434, against .684 and .392 with the old boundary examples. Most of the gain comes from the v5 rules, not the examples.
- **Ensemble.** The v5 ensemble (TEST α .734, κ .456) is below the best single v5 run.
- **143-call set: v5 does not improve, and applied gets much worse.** On TEST:
  - v5 31B zero-shot: α .677, κ .408, joint 28.8%.
  - v5 12B zero-shot: α .651, κ .430, joint 31.5%.
  - Baselines: v4 12B zero-shot α .663, κ .442, joint 42.5%; sheet-aligned 12B boundary few-shot α .700 (68 calls). The best α on all 143 calls is .711 (v4 12B zero-shot).
  - v5 31B zero-shot is .014 above v4 zero-shot on α. It is below on mean κ, joint exact, and the .700 and .711 references.
- **143-call set, where v5 is worse (TEST):**
  - Applied linear κ falls from .551 (v4 zero-shot) to .236–.341, and α from .581 to .242–.305. v5 gives applied 2 to 64–68% of TEST calls against 34% for the human codes; human 1 scored 2 on 25–28 of 73 calls, against 6 for v4.
  - Conceptual 2 rises to 40–47% against 26% for the humans (human 1 scored 2 on 12–18 calls). Conceptual linear κ still improves for v5 12B zero-shot (.541 against .387) but not for few-shot (.413) or 31B (.394).
  - Joint exact drops from 42.5% to 21.9–31.5%.
  - Governance falls for 31B and few-shot (.442 and .456 against .506). Critical improves (.41–.50 against .33).
  - On DEV and ALL, every v5 run is below v4 zero-shot (ALL overall α .643–.673 against .711).
- **Why.** The two coding sets apply the conceptual and applied 2 thresholds differently (`outputs/analysis/misses_n200_dev.md`, "Suspected inconsistencies"). v5 follows the 200-call set's threshold and so over-scores 2 on the 143-call set.
- **What `RESULTS.md` shows.** v5 31B zero-shot is the headline method for the 200-call file: TEST, plus all 200 calls. Its all-200 numbers differ slightly from the ALL rows above, which leave out the 10 DEV examples (α .756 on 200 against .751 on 190). For the 143-call file, `RESULTS.md` keeps v4 12B zero-shot as best (ALL α .711, TEST α .663), because v5 regresses there.
