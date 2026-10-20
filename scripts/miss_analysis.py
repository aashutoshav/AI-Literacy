#!/usr/bin/env python3
"""Miss analysis: model predictions vs human codes in data/coding.csv.

Writes a markdown report (confusion matrices + disagreeing calls for chosen
dimensions) and a CSV with one row per (call, dimension) disagreement.

Usage:
  python scripts/miss_analysis.py --preds outputs/preds_zeroshot_12b_n143.csv \
      --codes data/coding.csv --tag sheetalign_12b_zeroshot
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.schema import SCORE_DIMS  # noqa: E402


def normalize_codes(df: pd.DataFrame) -> pd.DataFrame:
    """Rename "conceptual (0-2)" style headers to the short dimension names."""
    ren = {f"{d} (0-2)": d for d in SCORE_DIMS if d not in df.columns and f"{d} (0-2)" in df.columns}
    return df.rename(columns=ren)

TEXT_COL = "AI-related sentences"


def _rel(p: Path) -> str:
    try:
        return str(Path(p).resolve().relative_to(ROOT))
    except ValueError:
        return str(p)


def excerpt(s: str, n: int = 300) -> str:
    s = " ".join(str(s or "").replace("•", " ").split())
    return s if len(s) <= n else s[: n - 1] + "…"


def md_cell(s: str) -> str:
    return str(s or "").replace("|", "\\|").replace("\n", " ")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--preds", type=Path, required=True)
    ap.add_argument("--codes", type=Path, default=ROOT / "data" / "coding.csv")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--detail-dims", nargs="+", default=["governance", "critical"])
    ap.add_argument("--outdir", type=Path, default=ROOT / "outputs" / "analysis")
    ap.add_argument("--patterns", type=Path, default=None, help="Optional markdown file inserted as a Patterns section")
    args = ap.parse_args()

    codes = normalize_codes(pd.read_csv(args.codes))
    preds = pd.read_csv(args.preds)
    m = codes.merge(preds, on="uid", how="inner")
    n = len(m)

    rows = []
    for _, r in m.iterrows():
        for d in SCORE_DIMS:
            h, p = int(r[d]), int(r[f"pred_{d}"])
            if h != p:
                rows.append({
                    "uid": r["uid"], "dimension": d, "human": h, "model": p,
                    "direction": "over" if p > h else "under",
                    "call_title": r.get("call_title", ""),
                    "model_evidence": r.get(f"evidence_{d}", "") if pd.notna(r.get(f"evidence_{d}", "")) else "",
                    "model_notes": r.get("notes", "") if pd.notna(r.get("notes", "")) else "",
                    "excerpt": excerpt(r[TEXT_COL], 400),
                })
    miss = pd.DataFrame(rows)
    args.outdir.mkdir(parents=True, exist_ok=True)
    csv_out = args.outdir / f"misses_{args.tag}.csv"
    miss.to_csv(csv_out, index=False)

    L = [f"# Miss analysis: {args.tag}", "",
         f"Predictions `{_rel(args.preds)}` compared with the human codes in `{_rel(args.codes)}`. n = {n} calls.",
         "Rows of each matrix are the human code; columns are the model score.", ""]
    if args.patterns and args.patterns.exists():
        L += [args.patterns.read_text().rstrip(), ""]
    L.append("## Disagreement counts")
    L.append("")
    L.append("| Dimension | Disagreements | Model higher | Model lower | Off by 2 |")
    L.append("|---|---|---|---|---|")
    for d in SCORE_DIMS:
        sub = miss[miss.dimension == d] if len(miss) else miss
        L.append(f"| {d} | {len(sub)} | {(sub.direction=='over').sum()} | {(sub.direction=='under').sum()} | {((sub.human-sub.model).abs()==2).sum()} |")
    L.append("")
    L.append("## Confusion matrices")
    for d in SCORE_DIMS:
        ct = pd.crosstab(m[d].astype(int), m[f"pred_{d}"].astype(int)).reindex(index=[0, 1, 2], columns=[0, 1, 2], fill_value=0)
        L += ["", f"### {d}", "", "| human \\ model | 0 | 1 | 2 | total |", "|---|---|---|---|---|"]
        for h in [0, 1, 2]:
            L.append(f"| {h} | " + " | ".join(str(ct.loc[h, p]) for p in [0, 1, 2]) + f" | {ct.loc[h].sum()} |")
        L.append("| total | " + " | ".join(str(ct[p].sum()) for p in [0, 1, 2]) + f" | {n} |")
    for d in args.detail_dims:
        sub = miss[miss.dimension == d].sort_values(["human", "model", "uid"])
        L += ["", f"## Disagreeing calls: {d} ({len(sub)})", "",
              "| uid | human | model | model evidence | excerpt of AI sentences |", "|---|---|---|---|---|"]
        for _, r in sub.iterrows():
            ev = excerpt(r.model_evidence, 220) or "(none, model scored 0)"
            L.append(f"| {r.uid} | {r.human} | {r.model} | {md_cell(ev)} | {md_cell(excerpt(r.excerpt, 260))} |")
    md_out = args.outdir / f"misses_{args.tag}.md"
    md_out.write_text("\n".join(L) + "\n")
    print(f"wrote {md_out} and {csv_out} ({len(miss)} disagreements)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
