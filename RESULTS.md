# AI Literacy Coding — Experiment Results

Living log of model-vs-human agreement on `coding.csv` (n=85 unless noted).  
Scores are 0–2 on **conceptual**, **critical**, **applied**, **governance**.

### How to read metrics
| Metric | Meaning |
|--------|---------|
| **Exact** | % of rows where model score == human score |
| **Adjacent** | % where \|model − human\| ≤ 1 |
| **QWK** | **Quadratic weighted kappa**: agreement between model and human on the 0–2 scale, corrected for chance. Exact matches count most; being off by 1 counts less; off by 2 counts least (quadratic weights). **0 ≈ chance**, **~0.4–0.6 moderate**, **~0.8+ strong**. Better than exact-% alone because it respects ordinal distance. |
| **Joint exact** | % of rows where *all four* dimensions match exactly |

---

## Run 1 — Gemma 4 12B-IT zero-shot (baseline)

| Field | Value |
|-------|-------|
| **Date** | 2026-09-16 (job finished ~05:35 ET) |
| **Model** | `google/gemma-4-12B-it` |
| **Prompt** | Zero-shot: rubric + JSON/evidence rules only (no labeled exemplars) |
| **Data** | Full gold set, `LIMIT=85` (`n_matched=85`) |
| **Cluster** | PACE ICE, partition `ice-gpu`, QoS `coc-ice` |
| **GPU** | NVIDIA **H200** (~141–150 GB) |
| **Job** | Slurm `5830112` |
| **Wall time** | ~21 minutes |
| **Env** | `scratch/conda_envs/ai_literacy`, `HF_HOME=scratch/hf_cache` |
| **Outputs** | `outputs/preds_zeroshot_12b_n85.csv`, `outputs/preds_zeroshot_12b_n85.jsonl` |
| **Metrics file** | `outputs/metrics/zeroshot_12b_n85.json` |

### Agreement vs `coding.csv`

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 64.7% | 98.8% | 0.519 |
| critical | 71.8% | 98.8% | 0.626 |
| **applied** | **28.2%** | 95.3% | **0.218** |
| governance | 81.2% | 98.8% | 0.587 |
| **joint (all 4)** | **9.4%** | — | — |

### Confusion highlights
- **Applied failure mode:** gold=`1` → pred=`2` in **54** rows (systematic over-coding).
- Other dims: mostly off-by-one; adjacent agreement is high everywhere.
- Governance exact is high partly because many gold labels are `0`.

### Takeaway
Usable ordinal signal on conceptual / critical / governance; **applied boundary (1 vs 2) is broken** under zero-shot.

---

## Run 2 — Gemma 4 12B-IT few-shot ×6

| Field | Value |
|-------|-------|
| **Date** | ~2026-09-20–22 (synced locally 2026-09-22) |
| **Model** | `google/gemma-4-12B-it` |
| **Prompt** | Few-shot with 6 gold exemplars (`configs/fewshot_exemplars.json`); exemplars **held out** of eval |
| **Data** | `n_matched=79` (85 − 6 held-out exemplars) |
| **Cluster** | PACE ICE, `ice-gpu` / H200 (same stack as Run 1) |
| **Outputs** | `outputs/preds_fewshot6_12b_n85.csv`, `outputs/preds_fewshot6_12b_n85.jsonl` |
| **Metrics file** | `outputs/metrics/fewshot6_12b_n85.json` |

### Agreement vs `coding.csv` (n=79)

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 63.3% | 98.7% | 0.559 |
| critical | 69.6% | 98.7% | 0.505 |
| **applied** | **44.3%** | **100%** | **0.459** |
| governance | 89.9% | 100% | 0.775 |
| **joint (all 4)** | **21.5%** | — | — |

### Confusion highlights
- Applied gold=`1` → pred=`2` drops from **54** (Run 1) to **39** (still the dominant error, but fewer).
- Applied exact +16 pp and QWK roughly doubles vs zero-shot 12B.
- Joint exact more than doubles (9.4% → 21.5%).
- Governance improves a lot (exact 81% → 90%, QWK 0.59 → 0.77).
- Critical is slightly weaker than zero-shot on exact/QWK (tradeoff).

### Takeaway
Few-shot **helps the applied 1-vs-2 boundary** and joint agreement without needing a larger model. Critical may need better exemplars or rubric wording.

---

## Run 3 — Gemma 4 31B-IT zero-shot

| Field | Value |
|-------|-------|
| **Date** | ~2026-09-20–22 (synced locally 2026-09-22) |
| **Model** | `google/gemma-4-31B-it` |
| **Prompt** | Zero-shot (same rubric/JSON rules as Run 1) |
| **Data** | Full gold set, `n_matched=85` |
| **Cluster** | PACE ICE, `ice-gpu` / H200 |
| **Outputs** | `outputs/preds_zeroshot_31b_n85.csv`, `outputs/preds_zeroshot_31b_n85.jsonl` |
| **Metrics file** | `outputs/metrics/zeroshot_31b_n85.json` |

### Agreement vs `coding.csv`

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 52.9% | 100% | 0.506 |
| critical | 76.5% | 98.8% | 0.663 |
| **applied** | **40.0%** | 97.6% | **0.354** |
| governance | 85.9% | 100% | 0.649 |
| **joint (all 4)** | **18.8%** | — | — |

### Confusion highlights
- Applied gold=`1` → pred=`2` still large (**46** rows), better than 12B zero-shot (54) but worse than 12B few-shot (39).
- Conceptual exact **drops** vs 12B zero-shot (64.7% → 52.9%): more gold=`1` → pred=`0` under-coding (24 cells).
- Critical and governance improve vs 12B zero-shot; joint exact roughly doubles (9.4% → 18.8%).

### Takeaway
Scaling to 31B zero-shot helps applied/joint vs 12B zero-shot, but **12B few-shot still beats 31B zero-shot on applied exact, applied QWK, and joint exact**. Size alone does not fix the applied boundary.

---

## Run 4 — Gemma 4 31B-IT few-shot ×6

| Field | Value |
|-------|-------|
| **Date** | 2026-09-22 (synced locally same day) |
| **Model** | `google/gemma-4-31B-it` |
| **Prompt** | Few-shot ×6 (same exemplars as Run 2; held out of eval) |
| **Data** | `n_matched=79` (85 − 6 held-out exemplars) |
| **Cluster** | PACE ICE, `ice-gpu` / H200 |
| **Outputs** | `outputs/preds_fewshot6_31b_n85.csv`, `outputs/preds_fewshot6_31b_n85.jsonl` |
| **Metrics file** | `outputs/metrics/fewshot6_31b_n85.json` |

### Agreement vs `coding.csv` (n=79)

| Dimension | Exact | Adjacent | QWK |
|-----------|------:|---------:|----:|
| conceptual | 44.3% | 100% | 0.472 |
| critical | 72.2% | 98.7% | 0.554 |
| **applied** | **45.6%** | **100%** | **0.481** |
| governance | 87.3% | 100% | 0.691 |
| **joint (all 4)** | **15.2%** | — | — |

### Confusion highlights
- Applied gold=`1` → pred=`2` stays at **39** rows — same count as 12B few-shot (no further cut from scaling).
- Applied edges Run 2 slightly (exact 45.6% vs 44.3%; QWK 0.481 vs 0.459).
- Conceptual collapses further (63.3% → 44.3%): gold=`1` → pred=`0` in **29** cells.
- Joint exact **falls** vs Run 2 (21.5% → 15.2%) because conceptual misses wipe out four-way matches.
- Critical recovers vs 12B few-shot; governance is a bit below Run 2.

### Takeaway
31B + few-shot is **not a clear win** over 12B + few-shot. Applied gains are tiny; conceptual under-coding and lower joint exact erase the benefit.

---

## Comparison table

| Run | Model | Prompt | n | Exact conceptual | Exact critical | Exact applied | Exact governance | Joint exact | Applied QWK |
|-----|-------|--------|--:|-----------------:|---------------:|--------------:|-----------------:|------------:|------------:|
| 1 | 12B-it | zero-shot | 85 | 64.7% | 71.8% | 28.2% | 81.2% | 9.4% | 0.218 |
| **2** | **12B-it** | **few-shot×6** | **79** | 63.3% | 69.6% | 44.3% | **89.9%** | **21.5%** | 0.459 |
| 3 | 31B-it | zero-shot | 85 | 52.9% | **76.5%** | 40.0% | 85.9% | 18.8% | 0.354 |
| 4 | 31B-it | few-shot×6 | 79 | 44.3% | 72.2% | **45.6%** | 87.3% | 15.2% | **0.481** |

---

## Conclusion

Across four prompted Gemma-4-IT coding runs on the same AI-literacy rubric:

1. **Applied is the bottleneck.** Adjacent accuracy is near ceiling on every dimension, but applied exact stays in the mid-40s at best. The recurring error is gold=`1` coded as `2` (54 → 39 → 46 → 39 rows across Runs 1–4). Models treat many mid-strength “we use AI in X” mentions as full operational deployment.

2. **Few-shot helps more than scale.** Moving from 12B zero-shot → 12B few-shot×6 roughly doubles applied QWK (0.22 → 0.46) and joint exact (9% → 22%). Moving 12B → 31B zero-shot helps applied less, and hurts conceptual exact.

3. **Best overall package so far: Run 2 (12B few-shot).** It leads joint exact and governance, and nearly ties the best applied scores. Run 4 (31B few-shot) is only marginally better on applied and **worse** on joint/conceptual — so size + exemplars did not stack cleanly.

4. **31B under-codes conceptual.** Both 31B runs push mid conceptual (`1`) toward `0`, which tanks joint exact even when other dims look fine.

5. **Practical next steps (if continuing):** sharpen applied 1-vs-2 exemplars and rubric wording (not another size bump); optionally add conceptual mid-band exemplars for 31B; consider a second-pass critic only on applied; keep 12B few-shot as the default coder until something clearly beats Run 2 on joint + applied together.

**Bottom line for the paper/project narrative:** prompted LLM coding can recover ordinal AI-literacy signal with high adjacent agreement, but **reliable applied mid-band coding needs better demonstration/rubric design more than a larger model.**
