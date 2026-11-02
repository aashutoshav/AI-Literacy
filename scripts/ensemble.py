#!/usr/bin/env python3
"""Per-dimension majority-vote ensemble over several prediction CSVs.

--method majority (default): the most common score per dimension. The first --preds
file is the anchor: on a tie (e.g. three runs giving 0, 1 and 2) the anchor's score is
used if it is among the tied scores, else the lower tied score.
--method mean: mean of the runs rounded to 0/1/2; an exact .5 goes toward the anchor. Only calls present
in every input are ensembled. Output has the usual preds CSV columns
(uid, notes, pred_<dim>, evidence_<dim>) so src.agreement / src.validate read it,
plus vote_<dim> columns showing each run's score.

Example (anchor = prompt v4 12B zero-shot):
  python scripts/ensemble.py \
      --preds outputs/preds_fix4_zeroshot_12b_n200.csv \
              outputs/preds_fix4_zeroshot_31b_n200.csv \
              outputs/preds_zeroshot_12b_n200.csv \
      --out outputs/preds_ens_v4x12b_v4x31b_sheet12b_n200.csv
"""
from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.schema import SCORE_DIMS  # noqa: E402


def vote(scores: list[int], anchor: int) -> int:
    """Most common score; a tie for most common goes to the anchor's score if it is
    among the tied scores (always the case with three runs), else the lower tied score."""
    counts = Counter(scores)
    top = max(counts.values())
    winners = sorted(s for s, c in counts.items() if c == top)
    if len(winners) == 1:
        return winners[0]
    return anchor if anchor in winners else winners[0]


def mean_round(scores: list[int], anchor: int) -> int:
    """Mean of the scores rounded to the nearest of 0/1/2; an exact .5 goes to the
    neighbour the anchor sits on (anchor <= lower -> lower, anchor >= upper -> upper)."""
    m = sum(scores) / len(scores)
    lo = int(m)
    if m - lo > 0.5:
        return lo + 1
    if m - lo < 0.5:
        return lo
    return lo + 1 if anchor > lo else lo


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--preds", nargs="+", type=Path, required=True, help="first file is the tie-break anchor")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--method", choices=["majority", "mean"], default="majority",
                    help="majority = per-dimension most common score; mean = mean of runs, rounded")
    ap.add_argument("--overwrite", action="store_true", help="allow replacing an existing ensemble file")
    args = ap.parse_args()
    if len(args.preds) < 2:
        ap.error("need at least two prediction files")
    if args.out.exists() and not args.overwrite:
        ap.error(f"{args.out} exists; refusing to overwrite")

    frames = []
    for i, p in enumerate(args.preds):
        df = pd.read_csv(p)
        missing = [f"pred_{d}" for d in SCORE_DIMS if f"pred_{d}" not in df.columns]
        if missing:
            ap.error(f"{p} lacks {missing}")
        frames.append(df.set_index("uid"))
    common = sorted(set.intersection(*(set(f.index) for f in frames)))
    dropped = {str(p): len(f) - len(common) for p, f in zip(args.preds, frames)}
    print(f"ensembling {len(args.preds)} runs on {len(common)} common calls; not in all runs: {dropped}")

    rows, n_tie, n_change = [], {d: 0 for d in SCORE_DIMS}, {d: 0 for d in SCORE_DIMS}
    for uid in common:
        row = {"uid": uid}
        notes = []
        for d in SCORE_DIMS:
            sc = [int(f.at[uid, f"pred_{d}"]) for f in frames]
            anchor = sc[0]
            counts = Counter(sc)
            top = max(counts.values())
            if args.method == "majority" and sum(c == top for c in counts.values()) > 1:
                n_tie[d] += 1
            win = (mean_round if args.method == "mean" else vote)(sc, anchor)
            if win != anchor:
                n_change[d] += 1
            row[f"pred_{d}"] = win
            row[f"vote_{d}"] = "/".join(str(s) for s in sc)
            ev = ""
            for f in frames:  # evidence from the first run that agrees with the vote
                if int(f.at[uid, f"pred_{d}"]) == win and f"evidence_{d}" in f.columns:
                    v = f.at[uid, f"evidence_{d}"]
                    ev = "" if pd.isna(v) else str(v)
                    break
            row[f"evidence_{d}"] = ev if win > 0 else ""
        notes.append(f"{args.method} ensemble of " + ", ".join(p.stem for p in args.preds))
        row["notes"] = "; ".join(notes)
        rows.append(row)

    cols = ["uid", "notes"] + [c for d in SCORE_DIMS for c in (f"pred_{d}", f"evidence_{d}")] + [f"vote_{d}" for d in SCORE_DIMS]
    args.out.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows)[cols].to_csv(args.out, index=False)
    print(f"tied top score (tie rule used): {n_tie}")
    print(f"ensemble differs from anchor: {n_change}")
    print(f"wrote {args.out} (n={len(rows)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
