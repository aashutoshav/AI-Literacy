"""Compare model predictions to human gold labels in coding.csv."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .metrics import full_report
from .schema import SCORE_DIMS, normalize_gold_frame


def _load_preds(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".jsonl":
        rows = []
        with path.open() as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                row = {"uid": obj.get("uid")}
                scores = obj.get("scores") or {}
                for d in SCORE_DIMS:
                    row[d] = scores.get(d)
                rows.append(row)
        return pd.DataFrame(rows)
    df = pd.read_csv(path)
    # Allow either flat columns or already matching names
    rename = {}
    for d in SCORE_DIMS:
        if f"pred_{d}" in df.columns and d not in df.columns:
            rename[f"pred_{d}"] = d
    if rename:
        df = df.rename(columns=rename)
    return df


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Validate AI-literacy preds vs gold coding.csv")
    p.add_argument("--preds", type=Path, required=True, help="preds CSV or JSONL")
    p.add_argument("--gold", type=Path, default=Path("coding.csv"))
    p.add_argument("--uid-col", default="uid")
    args = p.parse_args(argv)

    gold = normalize_gold_frame(pd.read_csv(args.gold))
    preds = _load_preds(args.preds)

    merged = gold.merge(preds, on=args.uid_col, suffixes=("_gold", "_pred"))
    if merged.empty:
        print("No overlapping uids between gold and preds.")
        return 1

    y_true, y_pred = {}, {}
    for d in SCORE_DIMS:
        gcol = d if d in merged.columns else f"{d}_gold"
        pcol = f"{d}_pred" if f"{d}_pred" in merged.columns else d
        # After merge with suffixes, gold/pred should be _gold/_pred if both had d
        if f"{d}_gold" in merged.columns:
            gcol = f"{d}_gold"
        if f"{d}_pred" in merged.columns:
            pcol = f"{d}_pred"
        y_true[d] = merged[gcol].astype(int).tolist()
        y_pred[d] = merged[pcol].astype(int).tolist()

    report = full_report(y_true, y_pred)
    print(f"n_matched={len(merged)}")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
