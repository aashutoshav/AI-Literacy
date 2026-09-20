#!/usr/bin/env bash
# Source this to activate ai_literacy + HF scratch caches.
SCRATCH="${SCRATCH:-/home/hice1/av84/scratch}"
ENV_PREFIX="${ENV_PREFIX:-$SCRATCH/conda_envs/ai_literacy}"
HF_CACHE="${HF_CACHE:-$SCRATCH/hf_cache}"

# Prefer existing conda on PATH / common Miniconda locations
if [[ -f "$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "$(conda info --base)/etc/profile.d/conda.sh"
elif [[ -f "$SCRATCH/miniconda3/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "$SCRATCH/miniconda3/etc/profile.d/conda.sh"
elif [[ -f "$SCRATCH/Miniconda3/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "$SCRATCH/Miniconda3/etc/profile.d/conda.sh"
fi

if [[ ! -d "$ENV_PREFIX" ]]; then
  echo "ERROR: env not found at $ENV_PREFIX"
  echo "Run: bash scripts/setup_hpc_env.sh"
  return 1 2>/dev/null || exit 1
fi

conda activate "$ENV_PREFIX"
export HF_HOME="$HF_CACHE"
export TRANSFORMERS_CACHE="$HF_HOME"
export HF_HUB_CACHE="$HF_HOME/hub"
export HF_DATASETS_CACHE="$HF_HOME/datasets"
mkdir -p "$HF_HUB_CACHE" "$HF_DATASETS_CACHE"
echo "Activated $ENV_PREFIX"
echo "HF_HOME=$HF_HOME"
echo "python=$(command -v python)"
