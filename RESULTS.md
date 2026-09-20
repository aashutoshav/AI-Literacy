# AI Literacy Coding — Experiment Results

Living log of model-vs-human agreement on `coding.csv` (n=85 unless noted).  
Scores are 0–2 on **conceptual**, **critical**, **applied**, **governance**.

### How to read metrics
| Metric | Meaning |
|--------|---------|
| **Exact** | % of rows where model score == human score |
| **Adjacent** | % where \|model − human\| ≤ 1 |
| **QWK** | Quadratic weighted kappa (chance-corrected; harder mistakes weigh more). Roughly: ~0 chance, ~0.4–0.6 moderate, ~0.8+ strong |
| **Joint exact** | % of rows where *all four* dimensions match exactly |

---

## Run 1 — Gemma 4 12B-IT zero-shot (baseline)

| Field | Value |
|-------|-------|
| **Date** | 2026-09-16 (job finished ~05:35 ET) |
| **Model** | `google/gemma-4-12B-it` |
| **Prompt** | Zero-shot: rubric + JSON/evidence rules only (no labeled exemplars) |
| **Data** | Full gold set, `LIMIT=85` |
| **Cluster** | PACE ICE, partition `ice-gpu`, QoS `coc-ice` |
| **GPU** | NVIDIA **H200** (~141–150 GB) |
| **Job** | Slurm `5830112` |
| **Wall time** | ~21 minutes |
| **Env** | `scratch/conda_envs/ai_literacy`, `HF_HOME=scratch/hf_cache` |
| **Outputs** | `outputs/preds_zeroshot_12b_n85.csv`, `outputs/preds_zeroshot_12b_n85.jsonl` |

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
Usable ordinal signal on conceptual / critical / governance; **applied boundary (1 vs 2) is broken** under zero-shot. Next runs should stress that boundary (few-shot) and compare **31B**.

---

## Planned / queued (fill in when done)

### Run 2 — 12B few-shot (6 exemplars)
- Status: **queued / pending**
- Model: `google/gemma-4-12B-it`
- Prompt: few-shot (`configs/fewshot_exemplars.json`, exemplars held out of eval by default)
- Tag expected: `fewshot6_12b_n85`
- Metrics: _TBD_

### Run 3 — 31B zero-shot
- Status: **queued / pending**
- Model: `google/gemma-4-31B-it`
- Tag expected: `zeroshot_31b_n85`
- Metrics: _TBD_

### Run 4 — 31B few-shot (6 exemplars)
- Status: **queued / pending**
- Model: `google/gemma-4-31B-it`
- Tag expected: `fewshot6_31b_n85`
- Metrics: _TBD_

---

## Comparison table (update after each run)

| Run | Model | Prompt | Exact conceptual | Exact critical | Exact applied | Exact governance | Joint exact | Applied QWK |
|-----|-------|--------|-----------------:|---------------:|--------------:|-----------------:|------------:|------------:|
| 1 | 12B-it | zero-shot | 64.7% | 71.8% | 28.2% | 81.2% | 9.4% | 0.218 |
| 2 | 12B-it | few-shot×6 | | | | | | |
| 3 | 31B-it | zero-shot | | | | | | |
| 4 | 31B-it | few-shot×6 | | | | | | |
