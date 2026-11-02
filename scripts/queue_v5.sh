#!/usr/bin/env bash
# Prompt v5 ("fix5") runs plus the v4 exemplar-swap control, on both coding sets.
# Few-shot uses configs/fewshot_exemplars_n200dev.json (10 DEV calls of the 200 set);
# --exclude-exemplars drops them from scoring on the 200 set (190 calls scored), none are in the 143 set.
# Usage (from project root on the cluster):  bash scripts/queue_v5.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p slurm outputs
EXD=configs/fewshot_exemplars_n200dev.json
q() {
  local name=$1 t=$2 csv=$3 limit=$4; shift 4
  local jid
  jid=$(sbatch --parsable --job-name="ail_${name}" --time="$t" --export="ALL,CSV=${csv},LIMIT=${limit},$*" scripts/run_code_gemma.sbatch)
  echo "queued ${name} (time ${t}) -> job ${jid}"
}
N2=data/coding_n200.csv; N1=data/coding.csv
q v5_zs12_n200   01:30:00 $N2 200 SIZE=12b,PROMPT_VERSION=v5,MODE=zeroshot,TAG=fix5_zeroshot_12b_n200
q v5_zs31_n200   02:30:00 $N2 200 SIZE=31b,PROMPT_VERSION=v5,MODE=zeroshot,TAG=fix5_zeroshot_31b_n200
q v5_v5_12_n200  03:00:00 $N2 200 SIZE=12b,PROMPT_VERSION=v5,MODE=vote5,NSAMPLES=5,TAG=fix5_vote5_zeroshot_12b_n200
q v5_fs12_n200   03:00:00 $N2 200 SIZE=12b,PROMPT_VERSION=v5,MODE=fewshot_boundary,SHOTS=10,EXEMPLARS_BOUNDARY=$EXD,TAG=fix5_fewshot_n200dev10_12b_n200
q v5_fs31_n200   05:00:00 $N2 200 SIZE=31b,PROMPT_VERSION=v5,MODE=fewshot_boundary,SHOTS=10,EXEMPLARS_BOUNDARY=$EXD,TAG=fix5_fewshot_n200dev10_31b_n200
q v4_fsd12_n200  03:00:00 $N2 200 SIZE=12b,PROMPT_VERSION=v4,MODE=fewshot_boundary,SHOTS=10,EXEMPLARS_BOUNDARY=$EXD,TAG=fix4_fewshot_n200dev10_12b_n200
q v5_zs12_n143   01:30:00 $N1 143 SIZE=12b,PROMPT_VERSION=v5,MODE=zeroshot,TAG=fix5_zeroshot_12b_n143
q v5_zs31_n143   02:30:00 $N1 143 SIZE=31b,PROMPT_VERSION=v5,MODE=zeroshot,TAG=fix5_zeroshot_31b_n143
q v5_fs12_n143   03:00:00 $N1 143 SIZE=12b,PROMPT_VERSION=v5,MODE=fewshot_boundary,SHOTS=10,EXEMPLARS_BOUNDARY=$EXD,TAG=fix5_fewshot_n200dev10_12b_n143
echo; echo "Monitor: squeue -u \$USER"
