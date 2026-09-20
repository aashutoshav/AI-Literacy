#!/usr/bin/env bash
# Idempotent conda env bootstrap for PACE ICE / av84 scratch layout.
set -euo pipefail

SCRATCH="${SCRATCH:-/home/hice1/av84/scratch}"
CONDA_ENVS="${CONDA_ENVS:-$SCRATCH/conda_envs}"
ENV_PREFIX="${ENV_PREFIX:-$CONDA_ENVS/ai_literacy}"
HF_CACHE="${HF_CACHE:-$SCRATCH/hf_cache}"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_VERSION="${PYTHON_VERSION:-3.11}"

echo "==> SCRATCH=$SCRATCH"
echo "==> ENV_PREFIX=$ENV_PREFIX"
echo "==> PROJECT_DIR=$PROJECT_DIR"

mkdir -p "$CONDA_ENVS" "$HF_CACHE/hub"

# Locate conda
if ! command -v conda >/dev/null 2>&1; then
  for candidate in \
    "$SCRATCH/miniconda3/etc/profile.d/conda.sh" \
    "$SCRATCH/Miniconda3/etc/profile.d/conda.sh" \
    "$HOME/miniconda3/etc/profile.d/conda.sh" \
    "$HOME/mambaforge/etc/profile.d/conda.sh"
  do
    if [[ -f "$candidate" ]]; then
      # shellcheck disable=SC1090
      source "$candidate"
      break
    fi
  done
fi

if ! command -v conda >/dev/null 2>&1; then
  echo "ERROR: conda not found. Install Miniconda under \$SCRATCH or module load it." >&2
  exit 1
fi

# shellcheck disable=SC1091
source "$(conda info --base)/etc/profile.d/conda.sh"

if [[ ! -d "$ENV_PREFIX" ]]; then
  echo "==> Creating env at $ENV_PREFIX (python=$PYTHON_VERSION)"
  conda create --prefix "$ENV_PREFIX" "python=$PYTHON_VERSION" pip -y
else
  echo "==> Env already exists at $ENV_PREFIX"
fi

conda activate "$ENV_PREFIX"

python -m pip install -U pip setuptools wheel

# Torch: skip if already importable; otherwise install CUDA 12.4 wheels (override with SKIP_TORCH=1)
if [[ "${SKIP_TORCH:-0}" != "1" ]]; then
  if python -c "import torch" 2>/dev/null; then
    echo "==> torch already installed: $(python -c 'import torch; print(torch.__version__)')"
  else
    echo "==> Installing torch (CUDA 12.4 wheels). Override index with TORCH_INDEX_URL if needed."
    TORCH_INDEX_URL="${TORCH_INDEX_URL:-https://download.pytorch.org/whl/cu124}"
    python -m pip install torch --index-url "$TORCH_INDEX_URL"
  fi
fi

echo "==> Installing requirements.txt"
python -m pip install -r "$PROJECT_DIR/requirements.txt"

ACTIVATE_HELPER="$PROJECT_DIR/env_activate.sh"
cat > "$ACTIVATE_HELPER" << INNER
#!/usr/bin/env bash
# Source this to activate ai_literacy + HF scratch caches.
SCRATCH="\${SCRATCH:-/home/hice1/av84/scratch}"
ENV_PREFIX="\${ENV_PREFIX:-$ENV_PREFIX}"
HF_CACHE="\${HF_CACHE:-$HF_CACHE}"

if [[ -f "\$(conda info --base 2>/dev/null)/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "\$(conda info --base)/etc/profile.d/conda.sh"
elif [[ -f "\$SCRATCH/miniconda3/etc/profile.d/conda.sh" ]]; then
  # shellcheck disable=SC1091
  source "\$SCRATCH/miniconda3/etc/profile.d/conda.sh"
fi

conda activate "\$ENV_PREFIX"
export HF_HOME="\$HF_CACHE"
export TRANSFORMERS_CACHE="\$HF_HOME"
export HF_HUB_CACHE="\$HF_HOME/hub"
export HF_DATASETS_CACHE="\$HF_HOME/datasets"
mkdir -p "\$HF_HUB_CACHE" "\$HF_DATASETS_CACHE"
echo "Activated \$ENV_PREFIX"
echo "HF_HOME=\$HF_HOME"
INNER
chmod +x "$ACTIVATE_HELPER"

echo "==> Wrote $ACTIVATE_HELPER"
echo "==> Done. Next:"
echo "    source $ACTIVATE_HELPER"
echo "    # HF token: reuse existing cache under $SCRATCH/hf_cache (skip login if already authenticated)"
echo "    source env_activate.sh"
