#!/usr/bin/env bash
# Remaining runs of the n=200 matrix (data/coding_n200.csv), on top of scripts/queue_n200.sh
# (which queued v4 zero 12B/31B, sheet zero 12B, v3 zero 12B, v4 vote5 12B).
# Matrix: prompt {sheet, v3, v4} x model {12B, 31B} x mode {zero-shot, vote5, few-shot 10 boundary exemplars}, plus v4 perdim 12B.
# Few-shot uses configs/fewshot_exemplars_boundary.json (TR calls, none in the n=200 file, so all 200 are scored).
# Usage (from project root on the cluster):  bash scripts/queue_n200_matrix.sh
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
# zero-shot 31B
q n200_sheet_zs31  02:30:00 SIZE=31b,PROMPT_VERSION=sheet,MODE=zeroshot,TAG=zeroshot_31b_n200
q n200_v3_zs31     02:30:00 SIZE=31b,PROMPT_VERSION=v3,MODE=zeroshot,TAG=fix3_zeroshot_31b_n200
# vote5
q n200_sheet_v5_12 03:00:00 SIZE=12b,PROMPT_VERSION=sheet,MODE=vote5,NSAMPLES=5,TAG=vote5_zeroshot_12b_n200
q n200_v3_v5_12    03:00:00 SIZE=12b,PROMPT_VERSION=v3,MODE=vote5,NSAMPLES=5,TAG=fix3_vote5_zeroshot_12b_n200
q n200_sheet_v5_31 08:00:00 SIZE=31b,PROMPT_VERSION=sheet,MODE=vote5,NSAMPLES=5,TAG=vote5_zeroshot_31b_n200
q n200_v3_v5_31    08:00:00 SIZE=31b,PROMPT_VERSION=v3,MODE=vote5,NSAMPLES=5,TAG=fix3_vote5_zeroshot_31b_n200
q n200_v4_v5_31    08:00:00 SIZE=31b,PROMPT_VERSION=v4,MODE=vote5,NSAMPLES=5,TAG=fix4_vote5_zeroshot_31b_n200
# few-shot, 10 boundary exemplars
for pv in sheet v3 v4; do
  case $pv in sheet) p="";; v3) p="fix3_";; v4) p="fix4_";; esac
  q n200_${pv}_fs12 03:00:00 SIZE=12b,PROMPT_VERSION=$pv,MODE=fewshot_boundary,SHOTS=10,TAG=${p}fewshot_boundary10_12b_n200
  q n200_${pv}_fs31 05:00:00 SIZE=31b,PROMPT_VERSION=$pv,MODE=fewshot_boundary,SHOTS=10,TAG=${p}fewshot_boundary10_31b_n200
done
# per-dimension prompts
q n200_v4_perdim12 05:00:00 SIZE=12b,PROMPT_VERSION=v4,MODE=perdim,TAG=fix4_perdim_zeroshot_12b_n200
echo; echo "Monitor: squeue -u \$USER"
