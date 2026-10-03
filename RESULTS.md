# AI Literacy Coding — Experiment Results

Living log of model-vs-human agreement. Scores in this file are **Round 2b** (loosened conceptual prompt) and a later **sheet-aligned rerun**, both finished 2026-10-03. Scores are 0–2 on **conceptual**, **critical**, **applied**, and **governance**.

Earlier runs used a smaller 85-row coding file (now archived) and then one strict-prompt 12B few-shot pass on the new sheet. Those numbers are not comparable to the current data/coding.csv results and are not reported here. The strict-prompt prediction file (job 6049275) was overwritten by job 6050889, so it cannot be re-scored from the current CSV.

## What is scored

- The human codes are in `data/coding.csv` from `Training_Compiled_9-28-2026.xlsx` (143 calls).
- **Models:** `google/gemma-4-12B-it` and `google/gemma-4-31B-it` on PACE ICE (NVIDIA H200).
- **Prompt (Round 2b):** conceptual was loosened so a 1 is any real AI capability, not only a mechanism. Zero-shot scores all 143 calls. Few-shot ×10 holds out the 10 exemplars in `configs/fewshot_exemplars.json`, so n=133.
- **Prompt (sheet-aligned rerun):** the coder is told to match the human coding sheet, not a stricter written guide; between 1 and 2, assign 1; score 2 only for substantial elaborated evidence. Same coding file and the same zero-shot n=143 / few-shot n=133 split.
- **Agreement** is exact match with the human codes in `data/coding.csv`, not with the written coding guide where the two disagree.

### How to read metrics

| Metric | Meaning |
|--------|---------|
| **Exact** | % of rows where model score == human score |
| **Adjacent** | % where \|model − human\| ≤ 1 |
| **QWK** | **Quadratic weighted kappa**: agreement between model and human on the 0–2 scale, corrected for chance. Exact matches count most; being off by 1 counts less; off by 2 counts least (quadratic weights). **0 ≈ chance**, **~0.4–0.6 moderate**, **~0.8+ strong**. Better than exact-% alone because it respects ordinal distance. |
| **Joint exact** | % of rows where *all four* dimensions match exactly |

Exact rates below are rounded to one decimal. Few-shot rows are not the same n as zero-shot rows (133 vs 143).

### How to reproduce

From the repo root:

```bash
python -m src.validate --preds <csv>
```

Prediction and metrics paths for each job are in the tables below.

## Round 2b — loosened conceptual prompt

The prediction CSVs named in this section were overwritten on the cluster by sheet-aligned jobs 6052529–6052532 (same filenames). Local copies at those paths were replaced by rsync on 2026-10-03. The pre-overwrite local files are in `outputs/round2b_loosened/`. The numbers below are the historical writeup and were not recomputed. The Round 2b metrics JSON files were not overwritten.

### Comparison

| Job | Model | Prompt | n | Exact conceptual | Exact critical | Exact applied | Exact governance | Joint exact |
|-----|-------|--------|--:|-----------------:|---------------:|--------------:|-----------------:|------------:|
| 6050888 | 12B-it | zero-shot | 143 | 78.3% | 72.0% | 59.4% | 76.9% | 28.7% |
| 6050889 | 12B-it | few-shot×10 | 133 | 56.4% | 73.7% | 59.4% | 75.9% | 15.0% |
| **6050890** | **31B-it** | **zero-shot** | **143** | 76.2% | 76.9% | **65.7%** | 76.2% | **32.2%** |
| 6050891 | 31B-it | few-shot×10 | 133 | 60.9% | 78.9% | 66.9% | 75.9% | 24.1% |

### 12B zero-shot — job 6050888

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

### 12B few-shot ×10 — job 6050889

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

### 31B zero-shot — job 6050890

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

### 31B few-shot ×10 — job 6050891

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

## Round 2b conclusion

Only 31B zero-shot (6050890) is at or above about 65% exact on every dimension. Applied is the dimension that just clears that bar (65.7%). Joint exact is still 32.2%, because a call has to be right on all four scores at once.

Loosening conceptual (a 1 is any real AI capability, not only a mechanism) fixed the zero-shot conceptual collapse. Few-shot made conceptual worse on both sizes (56.4% and 60.9%) and cut joint exact (15.0% and 24.1%, against 28.7% and 32.2% zero-shot). The 10 exemplars still teach some sheet/guide conflicts, so few-shot is not currently helping.

Applied human code 1 predicted as 2 is still the main remaining miss (43, 40, 29, and 22 rows).

These scores measure agreement with the human codes in `data/coding.csv`. Where the written coding guide is stricter than the sheet (for example TR009 conceptual, TR163 critical), matching the sheet is not the same as following the guide.

## Sheet-aligned rerun

Jobs finished 2026-10-03, all exit 0: 6052529 (12B zero-shot, 36:44, ended 01:56 ET), 6052530 (12B few-shot×10, 36:21, ended 01:56 ET), 6052531 (31B zero-shot, 43:24, ended 02:03 ET), 6052532 (31B few-shot×10, 46:45, ended 02:06 ET). The human coding is in `data/coding.csv`. The cluster copies of `src/prompts.py` (01:18 ET) and `configs/fewshot_exemplars.json` (01:19 ET) are the files these jobs loaded. Slurm logs wrote the same `outputs/preds_*_n143.csv` names as Round 2b, and the file timestamps match these jobs, so the Round 2b CSVs were overwritten.

### Comparison

| Job | Model | Prompt | n | Exact conceptual | Exact critical | Exact applied | Exact governance | Joint exact |
|-----|-------|--------|--:|-----------------:|---------------:|--------------:|-----------------:|------------:|
| **6052529** | **12B-it** | **zero-shot** | **143** | **81.1%** | **76.9%** | **73.4%** | **74.8%** | **42.7%** |
| 6052530 | 12B-it | few-shot×10 | 133 | 53.4% | 78.2% | 72.2% | 74.4% | 23.3% |
| 6052531 | 31B-it | zero-shot | 143 | 79.0% | 79.7% | 74.8% | 76.2% | 39.9% |
| 6052532 | 31B-it | few-shot×10 | 133 | 67.7% | 80.5% | 69.2% | 72.9% | 33.8% |

### Versus Round 2b (loosened prompt)

Round 2b numbers are the historical writeup above. They were not recomputed. Arrows point from Round 2b to this rerun.

| Run | Joint exact | Conceptual exact / QWK | Applied exact / QWK | Governance exact / QWK | Conceptual 1→0 | Applied 1→2 |
|-----|-------------|------------------------|---------------------|------------------------|----------------:|------------:|
| 12B zero-shot | 28.7% → 42.7% | 78.3% / 0.494 → 81.1% / 0.545 | 59.4% / 0.462 → 73.4% / 0.553 | 76.9% / 0.603 → 74.8% / 0.462 | 4 → 2 | 43 → 6 |
| 12B few-shot×10 | 15.0% → 23.3% | 56.4% / 0.379 → 53.4% / 0.384 | 59.4% / 0.494 → 72.2% / 0.616 | 75.9% / 0.514 → 74.4% / 0.270 | 33 → 36 | 40 → 12 |
| 31B zero-shot | 32.2% → 39.9% | 76.2% / 0.466 → 79.0% / 0.471 | 65.7% / 0.516 → 74.8% / 0.571 | 76.2% / 0.490 → 76.2% / 0.403 | 6 → 2 | 29 → 4 |
| 31B few-shot×10 | 24.1% → 33.8% | 60.9% / 0.421 → 67.7% / 0.424 | 66.9% / 0.576 → 69.2% / 0.507 | 75.9% / 0.493 → 72.9% / 0.335 | 28 → 17 | 22 → 8 |

### 12B zero-shot — job 6052529

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

### 12B few-shot ×10 — job 6052530

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

### 31B zero-shot — job 6052531

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

### 31B few-shot ×10 — job 6052532

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

## Sheet-aligned conclusion

The human coding is in `data/coding.csv`. These scores are agreement with that sheet, not with a stricter written guide.

Joint exact rose on every run versus Round 2b: 12B zero-shot 28.7% → 42.7%, 12B few-shot 15.0% → 23.3%, 31B zero-shot 32.2% → 39.9%, 31B few-shot 24.1% → 33.8%. The best joint score is now 12B zero-shot (6052529, 42.7%), ahead of 31B zero-shot (39.9%).

The applied human code 1 → pred 2 miss dropped on every run (43 → 6, 40 → 12, 29 → 4, 22 → 8). Applied exact rose with that: 59.4% → 73.4% (12B zero), 59.4% → 72.2% (12B few), 65.7% → 74.8% (31B zero), 66.9% → 69.2% (31B few). Applied QWK rose on the first three of those and fell on 31B few-shot (0.576 → 0.507).

Zero-shot conceptual stayed high and moved up a little (12B 78.3% / 0.494 → 81.1% / 0.545; 31B 76.2% / 0.466 → 79.0% / 0.471). Conceptual human code 1 → pred 0 fell on both zero-shot runs (4 → 2 and 6 → 2). Few-shot conceptual is still the weak cell. 12B few-shot got slightly worse (56.4% → 53.4%; 1→0 33 → 36). 31B few-shot improved (60.9% → 67.7%; 1→0 28 → 17) but remains below its own zero-shot conceptual (79.0% vs 67.7%) and below its own zero-shot joint (39.9% vs 33.8%).

Three runs are at or above 65% exact on every dimension: 12B zero-shot (lowest 73.4% applied), 31B zero-shot (lowest 74.8% applied), and 31B few-shot (lowest 67.7% conceptual). 12B few-shot is not (conceptual 53.4%).

Governance did not improve. Exact stayed in the low-to-mid 70s (76.9% → 74.8%, 75.9% → 74.4%, 76.2% → 76.2%, 75.9% → 72.9%). Governance QWK fell on every run (0.603 → 0.462, 0.514 → 0.270, 0.490 → 0.403, 0.493 → 0.335). The 12B few-shot governance QWK of 0.270 is the low point.

Few-shot still trails zero-shot on joint exact for both sizes. Matching the sheet is still not the same as following the written coding guide where the two disagree.
