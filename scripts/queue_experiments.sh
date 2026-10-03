#!/usr/bin/env bash
# Queue the current AI-literacy experiment on ICE (H200).
# Sheet-aligned rerun: four-run sweep after matching the coding sheet, especially applied 1 vs 2 (12B/31B × zeroshot/fewshot).
# Usage (from project root on the cluster, after rsync):
#   bash scripts/queue_experiments.sh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p slurm outputs

# 10 exemplars in configs/fewshot_exemplars.json. Exclusion happens before
# LIMIT in src/infer_gemma.py, so LIMIT=143 still scores every non-exemplar row.
SHOTS=10
LIMIT=143

echo "Submitting sheet-aligned four-run sweep (SHOTS=${SHOTS}, LIMIT=${LIMIT})..."

jid=$(sbatch --parsable --export=ALL,SIZE=12b,MODE=zeroshot,SHOTS=${SHOTS},LIMIT=${LIMIT} scripts/run_code_gemma.sbatch)
echo "queued 12b zeroshot -> job $jid"

jid=$(sbatch --parsable --export=ALL,SIZE=12b,MODE=fewshot,SHOTS=${SHOTS},LIMIT=${LIMIT} scripts/run_code_gemma.sbatch)
echo "queued 12b fewshot${SHOTS} -> job $jid"

jid=$(sbatch --parsable --export=ALL,SIZE=31b,MODE=zeroshot,SHOTS=${SHOTS},LIMIT=${LIMIT} scripts/run_code_gemma.sbatch)
echo "queued 31b zeroshot -> job $jid"

jid=$(sbatch --parsable --export=ALL,SIZE=31b,MODE=fewshot,SHOTS=${SHOTS},LIMIT=${LIMIT} scripts/run_code_gemma.sbatch)
echo "queued 31b fewshot${SHOTS} -> job $jid"

echo
echo "Monitor: squeue -u $USER"
echo "When done, validate (examples):"
echo "  python -m src.validate --preds outputs/preds_zeroshot_12b_n${LIMIT}.csv --gold data/coding.csv"
echo "  python -m src.validate --preds outputs/preds_fewshot${SHOTS}_12b_n${LIMIT}.csv --gold data/coding.csv"
echo "  python -m src.validate --preds outputs/preds_zeroshot_31b_n${LIMIT}.csv --gold data/coding.csv"
echo "  python -m src.validate --preds outputs/preds_fewshot${SHOTS}_31b_n${LIMIT}.csv --gold data/coding.csv"
