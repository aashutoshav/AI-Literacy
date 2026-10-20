#!/usr/bin/env bash
# Queue prompt v3 ("fix3") runs on ICE (H200), Gemma 4 12B, LIMIT=143.
#   fix3 zero-shot   single call per row (like the sheet-aligned baseline)
#   fix3 perdim      one prompt per dimension
#   fix3 vote5       single prompt, 5 samples, majority vote (ties -> lower)
# Usage (from project root on the cluster):  bash scripts/queue_fix3.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p slurm outputs
LIMIT=143
q() {
  local name=$1 t=$2; shift 2
  local jid
  jid=$(sbatch --parsable --job-name="ail_${name}" --time="$t" --export="ALL,SIZE=12b,LIMIT=${LIMIT},PROMPT_VERSION=v3,$*" scripts/run_code_gemma.sbatch)
  echo "queued ${name} (time ${t}) -> job ${jid}"
}
q fix3_zeroshot "${T_ZS:-01:30:00}"     MODE=zeroshot,TAG=fix3_zeroshot_12b_n${LIMIT}
q fix3_perdim   "${T_PERDIM:-05:00:00}" MODE=perdim,TAG=fix3_perdim_zeroshot_12b_n${LIMIT}
q fix3_vote5    "${T_VOTE5:-04:00:00}"  MODE=vote5,NSAMPLES=5,TAG=fix3_vote5_zeroshot_12b_n${LIMIT}
echo; echo "Monitor: squeue -u \$USER"
