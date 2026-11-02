#!/usr/bin/env bash
# Queue runs on the 10-30-2026 coding file (data/coding_n200.csv, n=200) on ICE (H200).
#   a. v4 zero-shot 12B        b. v4 zero-shot 31B
#   c. sheet-aligned zero-shot 12B   d. v3 zero-shot 12B   e. v4 vote5 12B
# Ensembles (a,b,c) and (a,b,d) are computed offline with scripts/ensemble.py.
# Usage (from project root on the cluster):  bash scripts/queue_n200.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p slurm outputs
CSV=data/coding_n200.csv
LIMIT=200
q() {
  local name=$1 t=$2; shift 2
  local jid
  jid=$(sbatch --parsable --job-name="ail_${name}" --time="$t" --export="ALL,CSV=${CSV},LIMIT=${LIMIT},$*" scripts/run_code_gemma.sbatch)
  echo "queued ${name} (time ${t}) -> job ${jid}"
}
q n200_v4_zs12   "${T_A:-01:30:00}" SIZE=12b,PROMPT_VERSION=v4,MODE=zeroshot,TAG=fix4_zeroshot_12b_n200
q n200_v4_zs31   "${T_B:-02:30:00}" SIZE=31b,PROMPT_VERSION=v4,MODE=zeroshot,TAG=fix4_zeroshot_31b_n200
q n200_sheet_zs12 "${T_C:-01:30:00}" SIZE=12b,PROMPT_VERSION=sheet,MODE=zeroshot,TAG=zeroshot_12b_n200
q n200_v3_zs12   "${T_D:-01:30:00}" SIZE=12b,PROMPT_VERSION=v3,MODE=zeroshot,TAG=fix3_zeroshot_12b_n200
q n200_v4_vote5  "${T_E:-03:00:00}" SIZE=12b,PROMPT_VERSION=v4,MODE=vote5,NSAMPLES=5,TAG=fix4_vote5_zeroshot_12b_n200
echo; echo "Monitor: squeue -u \$USER"
