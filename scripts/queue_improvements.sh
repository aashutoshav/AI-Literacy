#!/usr/bin/env bash
# Queue the four improvement experiments on ICE (H200), all Gemma 4 12B, sheet-aligned prompt as base.
#   perdim            one prompt per dimension (4 calls/row), greedy
#   vote5             single prompt, 5 samples (T=0.7, top_p=0.95), per-dimension majority vote, ties -> lower
#   perdim_vote5      per-dimension prompts x 5 samples, majority vote
#   fewshot_boundary  10 boundary exemplars (configs/fewshot_exemplars_boundary.json), held out -> n=133
# Each writes NEW files outputs/preds_<tag>.{csv,jsonl} (+ outputs/samples_<tag>.jsonl for vote modes);
# run_code_gemma.sbatch refuses to overwrite an existing preds CSV.
# Usage (from project root on the cluster, after rsync):  bash scripts/queue_improvements.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p slurm outputs
LIMIT=143
T_PERDIM="${T_PERDIM:-05:00:00}"
T_VOTE5="${T_VOTE5:-04:00:00}"
T_PERDIM_VOTE5="${T_PERDIM_VOTE5:-10:00:00}"
T_FEWSHOT="${T_FEWSHOT:-03:00:00}"

q() {  # name time exports...
  local name=$1 t=$2; shift 2
  local jid
  jid=$(sbatch --parsable --job-name="ail_${name}" --time="$t" --export="ALL,SIZE=12b,LIMIT=${LIMIT},$*" scripts/run_code_gemma.sbatch)
  echo "queued ${name} (time ${t}) -> job ${jid}"
}
q perdim           "$T_PERDIM"       MODE=perdim
q vote5            "$T_VOTE5"        MODE=vote5,NSAMPLES=5
q perdim_vote5     "$T_PERDIM_VOTE5" MODE=perdim_vote5,NSAMPLES=5
q fewshot_boundary "$T_FEWSHOT"      MODE=fewshot_boundary,SHOTS=10,TAG=fewshot_boundary10_12b_n133
echo
echo "Monitor: squeue -u \$USER"
