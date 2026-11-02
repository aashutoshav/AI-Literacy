#!/usr/bin/env python3
"""Score every run on both coding sets by split: TEST (headline), DEV and ALL.

Coding sets:
  n200: data/coding_n200.csv, split data/split_n200.csv, preds outputs/preds_*_n200.csv
  n143: data/coding.csv,      split data/split_n143.csv, preds outputs/preds_*_n143.csv and *_n133.csv
The 10 DEV exemplars in configs/fewshot_exemplars_n200dev.json are removed from DEV and ALL of
the n200 set for EVERY run (DEV = 90, ALL = 190), so runs that used them as few-shot examples
are compared on the same calls. TEST is never touched.

Also builds the v5 ensemble (majority of v5 12B zero, v5 31B zero, v5 12B few-shot; ties -> v5 12B zero)
when all three exist.

Per run and split: per-dimension linear kappa and ordinal alpha, mean linear kappa, mean per-dimension
alpha, overall-average ordinal alpha, ICC(A,1), joint exact, n.

Writes outputs/analysis/splits_comparison.csv and .md
Usage: python scripts/score_splits.py [--n-boot 1000]
"""
from __future__ import annotations

import argparse
import glob
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.agreement import compute, _clean_scores  # noqa: E402
from src.schema import SCORE_DIMS  # noqa: E402
from src.validate import _load_preds  # noqa: E402

SETS = {
    "n200": ("data/coding_n200.csv", "data/split_n200.csv", ["outputs/preds_*_n200.csv"]),
    "n143": ("data/coding.csv", "data/split_n143.csv", ["outputs/preds_*_n143.csv", "outputs/preds_*_n133.csv"]),
}
EXEMPLARS = "configs/fewshot_exemplars_n200dev.json"
V5_ENS = ["outputs/preds_fix5_zeroshot_12b_n200.csv", "outputs/preds_fix5_zeroshot_31b_n200.csv",
          "outputs/preds_fix5_fewshot_n200dev10_12b_n200.csv"]
V5_ENS_143 = ["outputs/preds_fix5_zeroshot_12b_n143.csv", "outputs/preds_fix5_zeroshot_31b_n143.csv",
              "outputs/preds_fix5_fewshot_n200dev10_12b_n143.csv"]


def f3(x):
    if x != x:
        return "–"
    s = f"{x:.3f}"
    return s.replace("0.", ".", 1) if s.startswith("0.") else s.replace("-0.", "-.", 1)


def codes_frame(path):
    df = pd.read_csv(path).rename(columns={f"{d} (0-2)": d for d in SCORE_DIMS})
    df = df[["uid", *SCORE_DIMS]].copy()
    for d in SCORE_DIMS:
        df[d] = _clean_scores(df[d])
    return df


def build_ensemble(members, out):
    if all(Path(m).exists() for m in members):
        subprocess.run([sys.executable, "scripts/ensemble.py", "--overwrite", "--out", out, "--preds", *members],
                       check=True, stdout=subprocess.DEVNULL)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot", type=int, default=1000)
    args = ap.parse_args()
    import os
    os.chdir(ROOT)
    build_ensemble(V5_ENS, "outputs/preds_ens_v5_trio_n200.csv")
    build_ensemble(V5_ENS_143, "outputs/preds_ens_v5_trio_n143.csv")
    ex_uids = {e["uid"] for e in json.load(open(EXEMPLARS))["exemplars"]}

    rows = []
    for setname, (codes_p, split_p, globs) in SETS.items():
        codes = codes_frame(codes_p).merge(pd.read_csv(split_p)[["uid", "split"]], on="uid")
        files = sorted({f for g in globs for f in glob.glob(g)})
        for f in files:
            run = Path(f).stem.replace("preds_", "")
            preds = _load_preds(Path(f))[["uid", *SCORE_DIMS]].copy()
            for d in SCORE_DIMS:
                preds[d] = _clean_scores(preds[d])
            m = codes.merge(preds, on="uid", suffixes=("_human", "_model")).dropna()
            if setname == "n200":
                m = m[~m.uid.isin(ex_uids)]
            for split in ("test", "dev", "all"):
                s = m if split == "all" else m[m.split == split]
                if len(s) < 10:
                    continue
                r = compute(s.reset_index(drop=True), args.n_boot, 20261031)
                d, o = r["dimensions"], r["overall_average"]
                row = {"set": setname, "run": run, "split": split, "n": r["n"],
                       "mean_lin_kappa": sum(d[k]["linear_kappa"] for k in SCORE_DIMS) / 4,
                       "mean_dim_alpha": sum(d[k]["kripp_alpha_ordinal"] for k in SCORE_DIMS) / 4,
                       "overall_alpha": o["kripp_alpha_ordinal"], "icc": o["icc_a1"],
                       "icc_lo": o["icc_a1_ci95_bootstrap"][0], "icc_hi": o["icc_a1_ci95_bootstrap"][1],
                       "joint_exact": o["exact_pct"], "mad": o["mean_abs_diff_composite"]}
                for k in SCORE_DIMS:
                    row[f"{k}_lin"] = d[k]["linear_kappa"]
                    row[f"{k}_alpha"] = d[k]["kripp_alpha_ordinal"]
                    row[f"{k}_exact"] = d[k]["exact_pct"]
                rows.append(row)
    df = pd.DataFrame(rows)
    Path("outputs/analysis").mkdir(parents=True, exist_ok=True)
    df.to_csv("outputs/analysis/splits_comparison.csv", index=False)

    md = ["# Agreement by split (TEST = headline; DEV = calls used for prompt writing; ALL)", "",
          "n200 set: DEV and ALL exclude the 10 DEV exemplars for every run (DEV 90, ALL 190). "
          "Lin κ = linear weighted κ; α = ordinal Krippendorff's α; overall α is on the four-dimension average; "
          "joint = all four dimensions match.", ""]
    for setname in SETS:
        for split in ("test", "dev", "all"):
            s = df[(df.set == setname) & (df.split == split)].sort_values("overall_alpha", ascending=False)
            if s.empty:
                continue
            md += [f"## {setname} · {split.upper()} (sorted by overall-average α)", "",
                   "| Run | n | Lin κ C | Lin κ Cr | Lin κ A | Lin κ G | Mean lin κ | α C | α Cr | α A | α G | Overall α | ICC | Joint |",
                   "|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|"]
            for _, r in s.iterrows():
                md.append(f"| {r.run} | {r.n} | " + " | ".join(f3(r[f'{k}_lin']) for k in SCORE_DIMS)
                          + f" | {f3(r.mean_lin_kappa)} | " + " | ".join(f3(r[f'{k}_alpha']) for k in SCORE_DIMS)
                          + f" | {f3(r.overall_alpha)} | {f3(r.icc)} | {r.joint_exact:.1f}% |")
            md.append("")
    Path("outputs/analysis/splits_comparison.md").write_text("\n".join(md) + "\n")
    print(f"scored {df.run.nunique()} runs; wrote outputs/analysis/splits_comparison.md/.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
