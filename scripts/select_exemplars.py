#!/usr/bin/env python3
"""Pick diverse few-shot exemplars from coding.csv for docs/prompts."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.schema import SCORE_DIMS, normalize_gold_frame, resolve_column, TEXT_COL_CANDIDATES  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=ROOT / "coding.csv")
    ap.add_argument("--n", type=int, default=6)
    args = ap.parse_args()

    df = normalize_gold_frame(pd.read_csv(args.csv))
    text_col = resolve_column(df.columns, TEXT_COL_CANDIDATES)
    dims = list(SCORE_DIMS)
    df["sig"] = df[dims].astype(int).astype(str).agg("-".join, axis=1)

    # one row per distinct score signature, then fill to n
    picked = df.groupby("sig", sort=False).head(1)
    if len(picked) < args.n:
        rest = df[~df.index.isin(picked.index)]
        picked = pd.concat([picked, rest.head(args.n - len(picked))])
    picked = picked.head(args.n)

    for _, row in picked.iterrows():
        excerpt = str(row[text_col]).replace("\n", " ")[:280]
        scores = {d: int(row[d]) for d in dims}
        print(f"uid={row.get('uid', '?')} company={row.get('company', '?')}")
        print(f"  scores={scores}")
        print(f"  excerpt={excerpt}...")
        print()


if __name__ == "__main__":
    main()
