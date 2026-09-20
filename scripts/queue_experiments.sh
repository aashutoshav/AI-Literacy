#!/usr/bin/env bash
# Queue the planned AI-literacy experiments on ICE (H200).
# Usage (from project root on the cluster, after rsync):
#   bash scripts/queue_experiments.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p slurm outputs

echo "Submitting experiments..."

# 1) 12B few-shot (main follow-up to zero-shot baseline)
jid1=$(sbatch --parsable --export=ALL,SIZE=12b,MODE=fewshot,SHOTS=6,LIMIT=85 scripts/run_code_gemma.sbatch)
echo "queued 12b fewshot6 -> job $jid1"

# 2) 31B zero-shot
jid2=$(sbatch --parsable --export=ALL,SIZE=31b,MODE=zeroshot,LIMIT=85 scripts/run_code_gemma.sbatch)
echo "queued 31b zeroshot -> job $jid2"

# 3) 31B few-shot
jid3=$(sbatch --parsable --export=ALL,SIZE=31b,MODE=fewshot,SHOTS=6,LIMIT=85 scripts/run_code_gemma.sbatch)
echo "queued 31b fewshot6 -> job $jid3"

echo
echo "Monitor: sq   or   squeue -u \$USER"
echo "When done, validate each:"
echo "  python -m src.validate --preds outputs/preds_fewshot6_12b_n85.csv --gold coding.csv"
echo "  python -m src.validate --preds outputs/preds_zeroshot_31b_n85.csv --gold coding.csv"
echo "  python -m src.validate --preds outputs/preds_fewshot6_31b_n85.csv --gold coding.csv"
