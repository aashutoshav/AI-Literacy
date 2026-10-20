#!/bin/bash
#SBATCH --job-name=ai_lit_gemma
#SBATCH --partition=ice-gpu
#SBATCH --account=coc
#SBATCH --qos=coc-ice
# RTX 6000 (~24GB) too small for 12B/31B BF16. Use H200.
#SBATCH --gres=gpu:h200:1
#SBATCH --nodes=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=slurm/%j.out
#SBATCH --error=slurm/%j.err

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"
mkdir -p slurm outputs

export HF_HOME="${HF_HOME:-/home/hice1/av84/scratch/hf_cache}"
export TRANSFORMERS_CACHE="$HF_HOME"
export HF_HUB_CACHE="$HF_HOME/hub"

if command -v module >/dev/null 2>&1; then
  module load "${CUDA_MODULE:-cuda}" 2>/dev/null || module load cuda/12.1 2>/dev/null || module load cuda/12.4 2>/dev/null || true
fi

echo "==> nvidia-smi"
nvidia-smi

if [[ -x "/home/hice1/av84/scratch/conda_envs/ai_literacy/bin/python" ]]; then
  PYTHON_EXEC="/home/hice1/av84/scratch/conda_envs/ai_literacy/bin/python"
elif [[ -x "/storage/ice1/7/6/av84/conda_envs/ai_literacy/bin/python" ]]; then
  PYTHON_EXEC="/storage/ice1/7/6/av84/conda_envs/ai_literacy/bin/python"
else
  echo "ERROR: ai_literacy conda env not found." >&2
  exit 1
fi

# SIZE: 12b | 31b
SIZE="${SIZE:-12b}"
case "$(echo "$SIZE" | tr '[:upper:]' '[:lower:]')" in
  12|12b) MODEL_ID="${MODEL_ID:-google/gemma-4-12B-it}" ;;
  31|31b) MODEL_ID="${MODEL_ID:-google/gemma-4-31B-it}" ;;
  *) echo "ERROR: unknown SIZE='$SIZE'" >&2; exit 1 ;;
esac

# MODE: zeroshot | fewshot          (original sheet-aligned runs; unchanged)
#       perdim                       one prompt per dimension, greedy
#       vote5                        single prompt, NSAMPLES samples (default 5), per-dimension majority vote
#       perdim_vote5                 per-dimension prompts, NSAMPLES samples each, majority vote
#       fewshot_boundary             few-shot with configs/fewshot_exemplars_boundary.json (held out)
MODE="${MODE:-zeroshot}"
SHOTS="${SHOTS:-0}"
LIMIT="${LIMIT:-143}"
EXEMPLARS="${EXEMPLARS:-configs/fewshot_exemplars.json}"
NSAMPLES="${NSAMPLES:-5}"
SAMPLE_TEMP="${SAMPLE_TEMP:-0.7}"
TOP_P="${TOP_P:-0.95}"
OUT_SAMPLES=""

case "$(echo "$MODE" | tr '[:upper:]' '[:lower:]')" in
  zero|zeroshot)
    SHOTS=0
    TAG="${TAG:-zeroshot_${SIZE}_n${LIMIT}}"
    EXTRA_ARGS=(--shots 0)
    ;;
  few|fewshot)
    SHOTS="${SHOTS:-6}"
    TAG="${TAG:-fewshot${SHOTS}_${SIZE}_n${LIMIT}}"
    EXTRA_ARGS=(--shots "$SHOTS" --exemplars "$EXEMPLARS" --exclude-exemplars)
    ;;
  perdim)
    SHOTS=0
    TAG="${TAG:-perdim_zeroshot_${SIZE}_n${LIMIT}}"
    EXTRA_ARGS=(--shots 0 --prompt-mode perdim)
    ;;
  vote5|vote)
    SHOTS=0
    TAG="${TAG:-vote${NSAMPLES}_zeroshot_${SIZE}_n${LIMIT}}"
    OUT_SAMPLES="outputs/samples_${TAG}.jsonl"
    EXTRA_ARGS=(--shots 0 --num-samples "$NSAMPLES" --sample-temperature "$SAMPLE_TEMP" --top-p "$TOP_P" --output-samples-jsonl "$OUT_SAMPLES")
    ;;
  perdim_vote5|perdim_vote)
    SHOTS=0
    TAG="${TAG:-perdim_vote${NSAMPLES}_zeroshot_${SIZE}_n${LIMIT}}"
    OUT_SAMPLES="outputs/samples_${TAG}.jsonl"
    EXTRA_ARGS=(--shots 0 --prompt-mode perdim --num-samples "$NSAMPLES" --sample-temperature "$SAMPLE_TEMP" --top-p "$TOP_P" --output-samples-jsonl "$OUT_SAMPLES")
    ;;
  fewshot_boundary)
    EXEMPLARS="${EXEMPLARS_BOUNDARY:-configs/fewshot_exemplars_boundary.json}"
    SHOTS="${SHOTS:-10}"
    TAG="${TAG:-fewshot_boundary${SHOTS}_${SIZE}_n${LIMIT}}"
    EXTRA_ARGS=(--shots "$SHOTS" --exemplars "$EXEMPLARS" --exclude-exemplars)
    ;;
  *)
    echo "ERROR: unknown MODE='$MODE' (zeroshot|fewshot|perdim|vote5|perdim_vote5|fewshot_boundary)" >&2
    exit 1
    ;;
esac

# PROMPT_VERSION: sheet (default, sheet-aligned baseline prompt) | v3 (fix3 rubric) | v4 (fix4: v3 with sheet-aligned applied)
PROMPT_VERSION="${PROMPT_VERSION:-sheet}"
if [[ "$PROMPT_VERSION" != "sheet" ]]; then
  EXTRA_ARGS+=(--prompt-version "$PROMPT_VERSION")
fi

OUT_JSONL="outputs/preds_${TAG}.jsonl"
OUT_CSV="outputs/preds_${TAG}.csv"

# Never overwrite an existing prediction file unless OVERWRITE=1.
if [[ -e "$OUT_CSV" && "${OVERWRITE:-0}" != "1" ]]; then
  echo "ERROR: $OUT_CSV already exists; refusing to overwrite (set OVERWRITE=1 or a new TAG)" >&2
  exit 1
fi

echo "==> torch CUDA check"
"$PYTHON_EXEC" -c "import torch; print('torch', torch.__version__); print('cuda_built', torch.version.cuda); print('cuda_available', torch.cuda.is_available()); assert torch.cuda.is_available(), 'CUDA unavailable'; print('device', torch.cuda.get_device_name(0))"

echo "Host=$(hostname)  PYTHON_EXEC=$PYTHON_EXEC  HF_HOME=$HF_HOME"
echo "SIZE=$SIZE  MODEL_ID=$MODEL_ID  MODE=$MODE  SHOTS=$SHOTS  LIMIT=$LIMIT  TAG=$TAG  NSAMPLES=$NSAMPLES  OUT_SAMPLES=$OUT_SAMPLES  PROMPT_VERSION=$PROMPT_VERSION"

# Human codes (round 2). v1 lives in archived/coding_v1_n85.csv and is not used here.
CSV="${CSV:-data/coding.csv}"
if [[ ! -f "$CSV" ]]; then echo "ERROR: coding CSV not found: $CSV" >&2; exit 1; fi

srun "$PYTHON_EXEC" -m src.infer_gemma \
  --config configs/default.yaml \
  --csv "$CSV" \
  --model-id "$MODEL_ID" \
  --limit "$LIMIT" \
  --output-jsonl "$OUT_JSONL" \
  --output-csv "$OUT_CSV" \
  "${EXTRA_ARGS[@]}"

echo "Job finished: $OUT_CSV"
