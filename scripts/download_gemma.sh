#!/usr/bin/env bash
# Download Gemma 4 IT checkpoints into scratch HF cache.
set -euo pipefail
SCRATCH="${SCRATCH:-/home/hice1/av84/scratch}"
export HF_HOME="${HF_HOME:-$SCRATCH/hf_cache}"
export TRANSFORMERS_CACHE="$HF_HOME"
export HF_HUB_CACHE="$HF_HOME/hub"
mkdir -p "$HF_HUB_CACHE"

MODELS=(
  "google/gemma-4-12B-it"
  "google/gemma-4-31B-it"
)

# Optional: SIZE=12b|31b|both (default both)
WHICH="${1:-both}"
case "$(echo "$WHICH" | tr '[:upper:]' '[:lower:]')" in
  12|12b) MODELS=("google/gemma-4-12B-it") ;;
  31|31b) MODELS=("google/gemma-4-31B-it") ;;
  both|all|"") ;;
  *) echo "usage: $0 [12b|31b|both]"; exit 1 ;;
esac

if ! command -v huggingface-cli >/dev/null 2>&1 && ! command -v hf >/dev/null 2>&1; then
  echo "ERROR: huggingface-cli not on PATH. source env_activate.sh first." >&2
  exit 1
fi

DL=(huggingface-cli download)
if command -v hf >/dev/null 2>&1; then
  DL=(hf download)
fi

echo "HF_HOME=$HF_HOME"
for m in "${MODELS[@]}"; do
  echo "==> downloading $m"
  "${DL[@]}" "$m"
done
echo "Done."
