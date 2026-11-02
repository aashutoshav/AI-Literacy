#!/usr/bin/env python3
"""Score every n=200 run (data/coding_n200.csv) and the offline ensembles.

For each prediction file that exists:
  * src.agreement -> outputs/metrics/agreement_<label>_n200.json
  * per-dimension score distribution (model vs human)
Then builds ensembles with scripts/ensemble.py (outputs/preds_ens_<name>_n200.csv) from
whatever members exist (an ensemble is skipped until all its members exist) and scores them.

Writes:
  outputs/analysis/n200_comparison.md   one table per run in the advisor's format + summary
  outputs/analysis/n200_comparison.csv  one row per run, all metrics
  outputs/analysis/n200_distributions.csv  share of 0/1/2 per dimension, human and each run

Usage (project root):  python scripts/score_n200.py [--n-boot 2000]
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import agreement  # noqa: E402
from src.schema import SCORE_DIMS  # noqa: E402
from src.validate import _load_preds  # noqa: E402

CODES = Path("data/coding_n200.csv")
O = "outputs"

# label: (prompt, model, mode, preds path)
RUNS = {
    "v4_zs_12b":     ("v4", "12B", "zero-shot", f"{O}/preds_fix4_zeroshot_12b_n200.csv"),
    "v4_zs_31b":     ("v4", "31B", "zero-shot", f"{O}/preds_fix4_zeroshot_31b_n200.csv"),
    "v3_zs_12b":     ("v3", "12B", "zero-shot", f"{O}/preds_fix3_zeroshot_12b_n200.csv"),
    "v3_zs_31b":     ("v3", "31B", "zero-shot", f"{O}/preds_fix3_zeroshot_31b_n200.csv"),
    "sheet_zs_12b":  ("sheet-aligned", "12B", "zero-shot", f"{O}/preds_zeroshot_12b_n200.csv"),
    "sheet_zs_31b":  ("sheet-aligned", "31B", "zero-shot", f"{O}/preds_zeroshot_31b_n200.csv"),
    "v4_vote5_12b":  ("v4", "12B", "vote5", f"{O}/preds_fix4_vote5_zeroshot_12b_n200.csv"),
    "v4_vote5_31b":  ("v4", "31B", "vote5", f"{O}/preds_fix4_vote5_zeroshot_31b_n200.csv"),
    "v3_vote5_12b":  ("v3", "12B", "vote5", f"{O}/preds_fix3_vote5_zeroshot_12b_n200.csv"),
    "v3_vote5_31b":  ("v3", "31B", "vote5", f"{O}/preds_fix3_vote5_zeroshot_31b_n200.csv"),
    "sheet_vote5_12b": ("sheet-aligned", "12B", "vote5", f"{O}/preds_vote5_zeroshot_12b_n200.csv"),
    "sheet_vote5_31b": ("sheet-aligned", "31B", "vote5", f"{O}/preds_vote5_zeroshot_31b_n200.csv"),
    "v4_fs10_12b":   ("v4", "12B", "few-shot (10 boundary)", f"{O}/preds_fix4_fewshot_boundary10_12b_n200.csv"),
    "v4_fs10_31b":   ("v4", "31B", "few-shot (10 boundary)", f"{O}/preds_fix4_fewshot_boundary10_31b_n200.csv"),
    "v3_fs10_12b":   ("v3", "12B", "few-shot (10 boundary)", f"{O}/preds_fix3_fewshot_boundary10_12b_n200.csv"),
    "v3_fs10_31b":   ("v3", "31B", "few-shot (10 boundary)", f"{O}/preds_fix3_fewshot_boundary10_31b_n200.csv"),
    "sheet_fs10_12b": ("sheet-aligned", "12B", "few-shot (10 boundary)", f"{O}/preds_fewshot_boundary10_12b_n200.csv"),
    "sheet_fs10_31b": ("sheet-aligned", "31B", "few-shot (10 boundary)", f"{O}/preds_fewshot_boundary10_31b_n200.csv"),
    "v4_perdim_12b": ("v4", "12B", "per-dimension", f"{O}/preds_fix4_perdim_zeroshot_12b_n200.csv"),
}

# name: (method, members (first = tie-break anchor), description)
ZS6 = ["v4_zs_12b", "v4_zs_31b", "v3_zs_12b", "v3_zs_31b", "sheet_zs_12b", "sheet_zs_31b"]
ENSEMBLES = {
    "v4_12b31b_sheet12b": ("majority", ["v4_zs_12b", "v4_zs_31b", "sheet_zs_12b"], "majority: v4 12B zero + v4 31B zero + sheet-aligned 12B zero"),
    "v4_12b31b_v3_12b":   ("majority", ["v4_zs_12b", "v4_zs_31b", "v3_zs_12b"], "majority: v4 12B zero + v4 31B zero + v3 12B zero"),
    "v4_trio":            ("majority", ["v4_zs_12b", "v4_zs_31b", "v4_vote5_12b"], "majority: v4 12B zero + v4 31B zero + v4 12B vote5"),
    "xprompt_12b":        ("majority", ["v4_zs_12b", "v3_zs_12b", "sheet_zs_12b"], "majority across prompts at 12B (v4/v3/sheet-aligned zero)"),
    "xprompt_31b":        ("majority", ["v4_zs_31b", "v3_zs_31b", "sheet_zs_31b"], "majority across prompts at 31B (v4/v3/sheet-aligned zero); tie -> v4 31B"),
    "zs6":                ("majority", ZS6, "majority of all six zero-shot runs (3 prompts x 2 models); tie -> v4 12B if tied, else lower"),
    "zs6_mean":           ("mean", ZS6, "mean of all six zero-shot runs, rounded; exact .5 toward v4 12B"),
    # Chosen before seeing n=200 results: the top runs by mean per-dimension linear kappa on the
    # old n=143 calls: v4 12B zero (.528), v3 12B vote5 (.527), and the best 31B run that exists
    # there, sheet-aligned 31B zero (.457). v3/v4 were never run at 31B on n=143.
    "best3_old":          ("majority", ["v4_zs_12b", "v3_vote5_12b", "sheet_zs_31b"], "majority of the best 3 on old n=143 data (v4 12B zero, v3 12B vote5, sheet-aligned 31B zero)"),
}

HUMAN_42 = {  # advisor's inter-coder table (Lee vs Elsie, n=42, older calls), for reference only
    "conceptual": (.817, .824, .848, "90.5% (38/42)"), "critical": (.700, .674, .711, "83.3% (35/42)"),
    "applied": (.824, .806, .830, "90.5% (38/42)"), "governance": (.705, .784, .751, "81.0% (34/42)"),
    "overall": (.738, .846, .858, "61.9% (26/42)"),
}


def _normalize(df: pd.DataFrame) -> pd.DataFrame:
    """'<dim> (0-2)' columns of data/coding_n200.csv -> '<dim>'."""
    return df.rename(columns={f"{d} (0-2)": d for d in SCORE_DIMS})


def f3(x):
    s = f"{x:.3f}"
    return s.replace("0.", ".", 1) if s.startswith("0.") else s.replace("-0.", "-.", 1)


def score(label: str, path: Path, n_boot: int) -> dict:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        agreement.main(["--preds", str(path), "--codes", str(CODES), "--tag", f"{label}_n200", "--n-boot", str(n_boot)])
    return json.loads((ROOT / O / "metrics" / f"agreement_{label}_n200.json").read_text())


def dist(df: pd.DataFrame) -> dict:
    out = {}
    for d in SCORE_DIMS:
        v = pd.to_numeric(df[d], errors="coerce")
        n = v.notna().sum()
        for k in (0, 1, 2):
            out[f"{d}_{k}"] = round(100 * (v == k).sum() / n, 1) if n else float("nan")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args()
    import os
    os.chdir(ROOT)

    codes = _normalize(pd.read_csv(CODES))
    rows, dists, sections, pending = [], [], [], []
    dists.append({"run": "human codes", **dist(codes)})

    table = dict(RUNS)
    for name, (method, members, desc) in ENSEMBLES.items():
        missing = [m for m in members if not Path(RUNS[m][3]).exists()]
        out = Path(f"{O}/preds_ens_{name}_n200.csv")
        if missing:
            pending.append(f"ensemble {name} (waiting on {', '.join(missing)})")
            continue
        subprocess.run([sys.executable, "scripts/ensemble.py", "--method", method, "--overwrite", "--out", str(out),
                        "--preds", *[RUNS[m][3] for m in members]], check=True, stdout=subprocess.DEVNULL)
        table[f"ens_{name}"] = ("ensemble", "mixed", desc, str(out))

    for label, (prompt, model, mode, path) in table.items():
        p = Path(path)
        if not p.exists():
            pending.append(f"{label} ({path})")
            continue
        r = score(label, p, args.n_boot)
        preds = _load_preds(p)
        inp = r["inputs"]
        d, o = r["dimensions"], r["overall_average"]
        row = {"run": label, "prompt": prompt, "model": model, "mode": mode, "preds": path, "n_used": r["n"],
               "n_dropped_invalid": inp["n_dropped_invalid"], "n_missing": inp["n_codes_without_pred"],
               "mean_dim_linear_kappa": sum(d[k]["linear_kappa"] for k in SCORE_DIMS) / 4}
        for k in SCORE_DIMS:
            for m in ("linear_kappa", "quadratic_kappa", "kripp_alpha_ordinal", "exact_pct"):
                row[f"{k}_{m}"] = d[k][m]
        for m in ("linear_kappa", "quadratic_kappa", "kripp_alpha_ordinal", "exact_pct", "icc_a1",
                  "mean_abs_diff_composite", "model_composite_mean", "human_composite_mean"):
            row[f"overall_{m}"] = o[m]
        row["overall_icc_ci_lo"], row["overall_icc_ci_hi"] = o["icc_a1_ci95_bootstrap"]
        rows.append(row)
        dists.append({"run": label, **dist(preds)})

        lines = [f"### {label} — {prompt}, {model}, {mode}", "",
                 f"`{path}`; n={r['n']} (dropped invalid {inp['n_dropped_invalid']}, missing {inp['n_codes_without_pred']})", "",
                 "| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |",
                 "|---|---:|---:|---:|---:|"]
        for k in SCORE_DIMS:
            x = d[k]
            lines.append(f"| {k.capitalize()} | {f3(x['linear_kappa'])} | {f3(x['quadratic_kappa'])} | {f3(x['kripp_alpha_ordinal'])} | {x['exact_pct']:.1f}% ({x['exact_k']}/{x['exact_n']}) |")
        lines.append(f"| Overall four-dimension average | {f3(o['linear_kappa'])} | {f3(o['quadratic_kappa'])} | {f3(o['kripp_alpha_ordinal'])} | {o['exact_pct']:.1f}% ({o['exact_k']}/{o['exact_n']}) |")
        lo, hi = o["icc_a1_ci95_bootstrap"]
        lines += ["", f"ICC(A,1) = {f3(o['icc_a1'])} (95% bootstrap CI {f3(lo)}–{f3(hi)}); mean |human − model| = {o['mean_abs_diff_composite']:.3f}; "
                  f"composite mean human {o['human_composite_mean']:.3f} vs model {o['model_composite_mean']:.3f}.", ""]
        sections.append("\n".join(lines))

    Path(f"{O}/analysis").mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(rows).sort_values("mean_dim_linear_kappa", ascending=False)
    df.to_csv(f"{O}/analysis/n200_comparison.csv", index=False)
    dd = pd.DataFrame(dists)
    dd.to_csv(f"{O}/analysis/n200_distributions.csv", index=False)

    md = ["# n=200 comparison (data/coding_n200.csv)", "",
          "Sorted by mean per-dimension linear weighted κ. Overall = four-dimension average (composite); joint exact = all four dimensions match.", "",
          "| Run | Prompt | Model | Mode | Con lin κ | Cri lin κ | App lin κ | Gov lin κ | Mean lin κ | Overall lin κ | Overall quad κ | Overall ord α | ICC(A,1) [95% CI] | MAD | Joint exact | n |",
          "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|"]
    for _, r in df.iterrows():
        md.append(f"| {r.run} | {r.prompt} | {r.model} | {r['mode']} | " + " | ".join(f3(r[f'{k}_linear_kappa']) for k in SCORE_DIMS)
                  + f" | {f3(r.mean_dim_linear_kappa)} | {f3(r.overall_linear_kappa)} | {f3(r.overall_quadratic_kappa)} | {f3(r.overall_kripp_alpha_ordinal)} | "
                  f"{f3(r.overall_icc_a1)} [{f3(r.overall_icc_ci_lo)}–{f3(r.overall_icc_ci_hi)}] | {r.overall_mean_abs_diff_composite:.3f} | {r.overall_exact_pct:.1f}% | {r.n_used} |")
    md += ["", "Human inter-coder reference (advisor table, Lee vs Elsie, n=42 older calls; lin κ / quad κ / ord α / exact):", ""]
    for k, v in HUMAN_42.items():
        md.append(f"- {k}: {f3(v[0])} / {f3(v[1])} / {f3(v[2])} / {v[3]}")
    md += ["", "## Score distributions (% of calls at 0 / 1 / 2)", "",
           "| Run | Conceptual | Critical | Applied | Governance |", "|---|---|---|---|---|"]
    for _, r in dd.iterrows():
        md.append(f"| {r.run} | " + " | ".join(f"{r[f'{k}_0']:.0f} / {r[f'{k}_1']:.0f} / {r[f'{k}_2']:.0f}" for k in SCORE_DIMS) + " |")
    md += ["", "## Ensembles", ""] + [f"- ens_{n}: {d} (first member breaks ties)" for n, (_, _, d) in ENSEMBLES.items()]
    md += ["", "## Per-run tables", ""] + sections
    if pending:
        md += ["## Pending (no preds yet)", ""] + [f"- {p}" for p in pending]
    Path(f"{O}/analysis/n200_comparison.md").write_text("\n".join(md) + "\n")
    print(f"scored {len(rows)} runs; pending {len(pending)}; wrote {O}/analysis/n200_comparison.md/.csv and n200_distributions.csv")
    if len(df):
        print(df[["run", "mean_dim_linear_kappa", "overall_kripp_alpha_ordinal", "overall_exact_pct"]].to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
