# AI Literacy — Earnings-Call Coding

Research scaffold for coding AI-literacy dimensions in CEO/executive earnings-call text with instruction-tuned **Google Gemma 4**, then validating against human labels in `data/coding.csv`.

## Goals

1. **Validate** the AI-literacy coding scheme (model vs human agreement).
2. **Measure** AI-literacy across companies from earnings-call AI-related sentences.
3. **Business angle**: market response to AI talk; compare female vs male CEOs (gender join table still needed — see `docs/grounding.md`).

## Data (`data/coding.csv`)

Round-2 gold (n=143), exported from `data/Training_Compiled_9-28-2026.xlsx` (sheet Coding). Rubric text is on that workbook's Rubric sheet and in the two coding-guide docx files in `data/`.

| Column | Description |
|--------|-------------|
| `uid` | Row id |
| `n_AI_sentences` | Count of AI-related sentences |
| `call_title` | Call identity (executive / company / call_date are not in this gold set) |
| `AI-related sentences` | Bullet-joined excerpt text |
| `conceptual (0-2)`, `critical (0-2)`, `applied (0-2)`, `governance (0-2)` | Human labels **0–2** |
| `overall` | Mean of the four scores |

v1 gold (n=85) is archived at `archived/coding_v1_n85.csv`. v1 few-shot exemplars are `archived/fewshot_exemplars_v1.json`. Do **not** overwrite `data/coding.csv`.

## Layout

```
README.md
requirements.txt / environment.yml
configs/default.yaml
docs/hpc_setup.md
docs/grounding.md
scripts/setup_hpc_env.sh
src/schema.py prompts.py metrics.py infer_gemma.py validate.py
outputs/
```

## Quickstart (local Mac)

```bash
cd "/Users/aashutosh/Documents/Academics - GaTech/Fall 2026/ai_literacy"
python3 -m venv .venv && source .venv/bin/activate
pip install -U pip
# Optional local torch (CPU ok for dry-run):
# pip install torch
pip install -r requirements.txt

# Syntax / dry-run without downloading Gemma:
python -m src.infer_gemma --limit 3 --dry-run --config configs/default.yaml

# After preds exist:
python -m src.validate --preds outputs/preds.csv --gold data/coding.csv
```

See `docs/grounding.md` for rubrics, JSON schema, and validation metrics.

## Quickstart (PACE ICE / Georgia Tech HPC)

Cluster layout (user `av84`):

| Resource | Path |
|----------|------|
| Scratch | `/home/hice1/av84/scratch` |
| Conda envs | `/home/hice1/av84/scratch/conda_envs` |
| Project | `/home/hice1/av84/scratch/ai_literacy` |
| HF cache | `/home/hice1/av84/scratch/hf_cache` |
| Login host (example) | `login-ice-gnr-1` |

```bash
# On the cluster (after syncing this repo to $SCRATCH/ai_literacy):
cd /home/hice1/av84/scratch/ai_literacy
bash scripts/setup_hpc_env.sh
source /home/hice1/av84/scratch/ai_literacy/env_activate.sh
# Accept Gemma license on HF + huggingface-cli login
python -m src.infer_gemma --config configs/default.yaml --limit 10
```

Full conda / CUDA / Slurm details: **`docs/hpc_setup.md`**.

## Default model

- **Default:** `google/gemma-4-12B-it` (good fit for HPC GPU jobs).
- **Lighter:** E4B IT variants (less VRAM).
- **Heavier:** 31B IT or 26B-A4B MoE (more VRAM).

Stack: `transformers` + `accelerate`. Prefer Transformers **≥ 5.5** for Gemma 4.

## Docs

- [`docs/hpc_setup.md`](docs/hpc_setup.md) — conda env, CUDA, HF cache, Slurm
- [`docs/grounding.md`](docs/grounding.md) — rubrics, prompts, agreement metrics

## Round 2 — one run (PACE)

From the cluster project root, after rsync. This queues **only** Gemma 4 12B-it few-shot (10 exemplars). `LIMIT=143` is applied after exemplar exclusion, so every non-exemplar row is scored. Do not queue 31B or zero-shot this round.

```bash
cd /home/hice1/av84/scratch/ai_literacy
bash scripts/queue_experiments.sh
# equivalent:
# sbatch --export=ALL,SIZE=12b,MODE=fewshot,SHOTS=10,LIMIT=143 scripts/run_code_gemma.sbatch
```

## Model choice (flag)

Default config file still lists `google/gemma-4-31B-it`; the sbatch script picks the size. Round 2 uses 12B-it only:

```bash
# current experiment
SIZE=12b MODE=fewshot SHOTS=10 LIMIT=143 sbatch --export=ALL,SIZE=12b,MODE=fewshot,SHOTS=10,LIMIT=143 scripts/run_code_gemma.sbatch
```

Download both into scratch cache (reuse existing HF auth):

```bash
source env_activate.sh
bash scripts/download_gemma.sh both
```


## Results log

Experiment metrics are accumulated in **[RESULTS.md](RESULTS.md)** — append each new run there.
