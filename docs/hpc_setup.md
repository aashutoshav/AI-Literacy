# HPC setup — PACE ICE (Georgia Tech)

Target layout for user **`av84`**:

| Item | Path / value |
|------|----------------|
| Login host (example) | `login-ice-gnr-1` |
| Scratch | `/home/hice1/av84/scratch` |
| Conda envs | `/home/hice1/av84/scratch/conda_envs` |
| Project | `/home/hice1/av84/scratch/ai_literacy` |
| HF cache | `/home/hice1/av84/scratch/hf_cache` |

Miniconda installer and `conda_envs` / `hf_cache` folders may already exist under scratch.

## 1. Sync the project

```bash
# From your Mac (example with rsync over SSH):
# rsync -avz --exclude '.venv' --exclude 'outputs/*' \
#   "/Users/aashutosh/Documents/Academics - GaTech/Fall 2026/ai_literacy/" \
#   av84@login-ice-gnr-1:/home/hice1/av84/scratch/ai_literacy/
```

Keep `coding.csv` intact; never regenerate it on the cluster from model output.

## 2. Create the conda env (idempotent script)

Preferred:

```bash
cd /home/hice1/av84/scratch/ai_literacy
bash scripts/setup_hpc_env.sh
```

Manual equivalent:

```bash
export SCRATCH=/home/hice1/av84/scratch
export CONDA_ENVS=$SCRATCH/conda_envs
# Ensure conda is on PATH (Miniconda under scratch, or module):
#   source $SCRATCH/miniconda3/etc/profile.d/conda.sh
#   # or: module load anaconda3  # if provided

conda create --prefix "$CONDA_ENVS/ai_literacy" python=3.11 -y
conda activate "$CONDA_ENVS/ai_literacy"

# --- PyTorch (CUDA) ---
# Pick the CUDA build that matches the GPU node / module you load.
# Sensible default: CUDA 12.4 wheels from pytorch.org
pip install torch --index-url https://download.pytorch.org/whl/cu124
# Alternative: conda-forge pytorch with cuda-version=12.*

pip install -r requirements.txt
```

## 3. Hugging Face cache on scratch

Always point caches at scratch (home quotas are small):

```bash
export HF_HOME=/home/hice1/av84/scratch/hf_cache
export TRANSFORMERS_CACHE=$HF_HOME
export HF_HUB_CACHE=$HF_HOME/hub
mkdir -p "$HF_HUB_CACHE"
```

`scripts/setup_hpc_env.sh` writes `env_activate.sh` that exports these.

## 4. Gated Gemma models (license + token)

Many Gemma checkpoints require accepting the license on the model card and authenticating:

```bash
source /home/hice1/av84/scratch/ai_literacy/env_activate.sh
huggingface-cli login
# Paste a read token from https://huggingface.co/settings/tokens
# Also open the model page and accept the license for google/gemma-4-12B-it
```

## 5. Activate on login vs in Slurm

**Interactive login node:**

```bash
source /home/hice1/av84/scratch/ai_literacy/env_activate.sh
```

**Inside a job script:** source the same helper after any `module load` lines so CUDA libs and the env agree.

## 6. Example `sbatch` (matches your ICE sample)

Use `scripts/run_code_gemma.sbatch`. Key flags from your working jobs:

- `--partition=ice-gpu`
- `--account=coc`
- `--qos=coc-ice`
- `HF_HOME=/home/hice1/av84/scratch/hf_cache`
- Python via conda env bin (scratch prefix **or** `/storage/ice1/7/6/av84/conda_envs/<env>/bin/python`)

```bash
cd /home/hice1/av84/scratch/ai_literacy
mkdir -p slurm
LIMIT=10 sbatch scripts/run_code_gemma.sbatch
LIMIT=85 sbatch scripts/run_code_gemma.sbatch
```

If `--gres=gpu:1` is rejected, try `#SBATCH --gres=gpu:h200:1` (or the GPU type your allocation allows).

## 7. After the job

```bash
source env_activate.sh
python -m src.validate --preds outputs/preds.csv --gold coding.csv
```

## Path note

On ICE, scratch often resolves under `/storage/ice1/...`. Your `c21u` env used:

`/storage/ice1/7/6/av84/conda_envs/c21u/bin/python`

Creating `--prefix $SCRATCH/conda_envs/ai_literacy` should yield an equivalent path under storage. The sbatch script checks both locations.

## CUDA not available in a GPU job

If `.out` says `CUDA not available` while on `ice-gpu`:

1. `scancel` the job (CPU 12B is uselessly slow).
2. Reinstall CUDA PyTorch in the env (example cu124 — match cluster CUDA):

```bash
source env_activate.sh
python -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available())"
pip uninstall -y torch torchvision torchaudio
pip install torch --index-url https://download.pytorch.org/whl/cu124
```

3. Confirm inside a GPU allocation (not only on the login node) with `nvidia-smi` and `torch.cuda.is_available()`.

