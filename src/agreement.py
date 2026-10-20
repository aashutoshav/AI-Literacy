"""Model-vs-human agreement in the same format as the human inter-rater table.

Compares one predictions file against the human codes in data/coding.csv and reports,
per dimension (conceptual, critical, applied, governance):

  * linear weighted Cohen's kappa   (sklearn cohen_kappa_score, weights="linear", labels 0..2)
  * quadratic weighted Cohen's kappa (weights="quadratic", labels 0..2; same as src.validate QWK)
  * ordinal Krippendorff's alpha     (`krippendorff` package, two raters: human and model,
                                      value_domain 0..2)
  * exact agreement                  (% and k/n)

and an "overall four-dimension average" row computed on each case's mean of the four
scores (the composite, values 0, 0.25, ..., 2):

  * linear / quadratic kappa: composite mapped to 9 ordered categories (mean * 4 -> 0..8)
  * Krippendorff's alpha: ordinal over the 9 composite values (also interval, reported separately)
  * exact: all four dimensions match on the case (= "joint exact")

plus ICC(A,1) (two-way random, absolute agreement, single measure; McGraw & Wong) on the
composite with a percentile bootstrap 95% CI over cases, and the mean absolute difference
of the composite.

Rows whose prediction is missing, non-numeric, or outside {0,1,2} on ANY dimension are
dropped for every metric (so all dimensions use the same cases) and counted in the output.

Usage:
    python -m src.agreement --preds outputs/preds_zeroshot_12b_n143.csv --codes data/coding.csv \
        --tag sheetalign_zeroshot_12b
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score

from .schema import SCORE_DIMS, normalize_gold_frame
from .validate import _load_preds

try:
    import krippendorff
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pip install krippendorff  (needed for Krippendorff's alpha)") from exc

LABELS = [0, 1, 2]
COMPOSITE_DOMAIN = [i / 4 for i in range(9)]  # 0, 0.25, ..., 2.0


def _clean_scores(series: pd.Series) -> pd.Series:
    """Numeric score in {0,1,2}, else NaN."""
    s = pd.to_numeric(series, errors="coerce")
    ok = s.isin(LABELS)
    return s.where(ok)


def icc_a1(x: np.ndarray, y: np.ndarray) -> float:
    """ICC(A,1): two-way random effects, absolute agreement, single rater (k=2 raters)."""
    data = np.column_stack([x, y]).astype(float)
    n, k = data.shape
    grand = data.mean()
    ss_rows = k * ((data.mean(axis=1) - grand) ** 2).sum()
    ss_cols = n * ((data.mean(axis=0) - grand) ** 2).sum()
    ss_tot = ((data - grand) ** 2).sum()
    ss_err = ss_tot - ss_rows - ss_cols
    msr = ss_rows / (n - 1)
    msc = ss_cols / (k - 1)
    mse = ss_err / ((n - 1) * (k - 1))
    denom = msr + (k - 1) * mse + k * (msc - mse) / n
    return float((msr - mse) / denom) if denom != 0 else float("nan")


def kalpha(h, m, level: str, domain) -> float:
    return float(
        krippendorff.alpha(
            reliability_data=np.vstack([np.asarray(h, float), np.asarray(m, float)]),
            level_of_measurement=level,
            value_domain=list(domain),
        )
    )


def compute(merged: pd.DataFrame, n_boot: int, seed: int) -> dict:
    n = len(merged)
    out: dict = {"n": n, "dimensions": {}}
    for d in SCORE_DIMS:
        h = merged[f"{d}_human"].astype(int).to_numpy()
        m = merged[f"{d}_model"].astype(int).to_numpy()
        k = int((h == m).sum())
        out["dimensions"][d] = {
            "linear_kappa": float(cohen_kappa_score(h, m, weights="linear", labels=LABELS)),
            "quadratic_kappa": float(cohen_kappa_score(h, m, weights="quadratic", labels=LABELS)),
            "kripp_alpha_ordinal": kalpha(h, m, "ordinal", LABELS),
            "exact_k": k,
            "exact_n": n,
            "exact_pct": 100.0 * k / n,
        }

    H = merged[[f"{d}_human" for d in SCORE_DIMS]].astype(int).to_numpy()
    M = merged[[f"{d}_model" for d in SCORE_DIMS]].astype(int).to_numpy()
    hc, mc = H.mean(axis=1), M.mean(axis=1)
    hcat, mcat = np.rint(hc * 4).astype(int), np.rint(mc * 4).astype(int)
    joint_k = int((H == M).all(axis=1).sum())

    icc = icc_a1(hc, mc)
    rng = np.random.default_rng(seed)
    boots = []
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        v = icc_a1(hc[idx], mc[idx])
        if np.isfinite(v):
            boots.append(v)
    lo, hi = np.percentile(boots, [2.5, 97.5]) if boots else (float("nan"), float("nan"))

    icc_pg = None
    try:
        import pingouin as pg

        long = pd.DataFrame(
            {
                "case": np.concatenate([np.arange(n), np.arange(n)]),
                "rater": ["human"] * n + ["model"] * n,
                "score": np.concatenate([hc, mc]),
            }
        )
        t = pg.intraclass_corr(data=long, targets="case", raters="rater", ratings="score")
        row = t[t["Type"].isin(["ICC2", "ICC(A,1)"])]
        icc_pg = float(row["ICC"].iloc[0])
    except Exception:  # noqa: BLE001  (pingouin optional; direct formula is the reported value)
        icc_pg = None

    out["overall_average"] = {
        "linear_kappa": float(cohen_kappa_score(hcat, mcat, weights="linear", labels=list(range(9)))),
        "quadratic_kappa": float(cohen_kappa_score(hcat, mcat, weights="quadratic", labels=list(range(9)))),
        "kripp_alpha_ordinal": kalpha(hc, mc, "ordinal", COMPOSITE_DOMAIN),
        "kripp_alpha_interval": kalpha(hc, mc, "interval", COMPOSITE_DOMAIN),
        "exact_k": joint_k,
        "exact_n": n,
        "exact_pct": 100.0 * joint_k / n,
        "icc_a1": icc,
        "icc_a1_pingouin_icc2": icc_pg,
        "icc_a1_ci95_bootstrap": [float(lo), float(hi)],
        "bootstrap_resamples": n_boot,
        "bootstrap_valid": len(boots),
        "bootstrap_seed": seed,
        "mean_abs_diff_composite": float(np.abs(hc - mc).mean()),
        "human_composite_mean": float(hc.mean()),
        "model_composite_mean": float(mc.mean()),
    }
    return out


def _fmt(x: float) -> str:
    s = f"{x:.3f}"
    return s.replace("0.", ".", 1) if s.startswith("0.") else s.replace("-0.", "-.", 1)


def print_table(res: dict) -> None:
    print("| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |")
    print("|---|---:|---:|---:|---:|")
    for d in SCORE_DIMS:
        r = res["dimensions"][d]
        print(
            f"| {d.capitalize()} | {_fmt(r['linear_kappa'])} | {_fmt(r['quadratic_kappa'])} | "
            f"{_fmt(r['kripp_alpha_ordinal'])} | {r['exact_pct']:.1f}% ({r['exact_k']}/{r['exact_n']}) |"
        )
    o = res["overall_average"]
    print(
        f"| Overall four-dimension average | {_fmt(o['linear_kappa'])} | {_fmt(o['quadratic_kappa'])} | "
        f"{_fmt(o['kripp_alpha_ordinal'])} | {o['exact_pct']:.1f}% ({o['exact_k']}/{o['exact_n']}) |"
    )
    lo, hi = o["icc_a1_ci95_bootstrap"]
    print(
        f"\nComposite: ICC(A,1) = {_fmt(o['icc_a1'])} (95% bootstrap CI {_fmt(lo)}–{_fmt(hi)}, "
        f"{o['bootstrap_resamples']} resamples, seed {o['bootstrap_seed']}); "
        f"pingouin ICC(A,1) = {o['icc_a1_pingouin_icc2']}; "
        f"interval α = {_fmt(o['kripp_alpha_interval'])}; "
        f"mean |human − model| = {o['mean_abs_diff_composite']:.3f} points (0–2)."
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Model-vs-human agreement (kappa, alpha, ICC)")
    p.add_argument("--preds", type=Path, required=True)
    p.add_argument("--codes", type=Path, default=Path("data/coding.csv"))
    p.add_argument("--tag", default=None, help="writes outputs/metrics/agreement_<tag>.json")
    p.add_argument("--n-boot", type=int, default=2000)
    p.add_argument("--seed", type=int, default=20261019)
    args = p.parse_args(argv)

    codes = normalize_gold_frame(pd.read_csv(args.codes))[["uid", *SCORE_DIMS]]
    preds = _load_preds(args.preds)[["uid", *SCORE_DIMS]]
    n_codes, n_preds = len(codes), len(preds)

    for d in SCORE_DIMS:
        codes[d] = _clean_scores(codes[d])
        preds[d] = _clean_scores(preds[d])
    bad_codes = int(codes[list(SCORE_DIMS)].isna().any(axis=1).sum())

    merged = codes.merge(preds, on="uid", suffixes=("_human", "_model"))
    n_matched = len(merged)
    cols = [f"{d}_{s}" for d in SCORE_DIMS for s in ("human", "model")]
    invalid = merged[cols].isna().any(axis=1)
    dropped_uids = merged.loc[invalid, "uid"].tolist()
    merged = merged.loc[~invalid].reset_index(drop=True)

    res = compute(merged, args.n_boot, args.seed)
    res["inputs"] = {
        "preds": str(args.preds),
        "codes": str(args.codes),
        "n_codes": n_codes,
        "n_codes_invalid": bad_codes,
        "n_preds": n_preds,
        "n_matched_uid": n_matched,
        "n_dropped_invalid": len(dropped_uids),
        "dropped_uids": dropped_uids,
        "n_codes_without_pred": n_codes - n_matched,
    }

    print(
        f"preds={args.preds}  codes={n_codes} preds_rows={n_preds} matched={n_matched} "
        f"dropped_invalid={len(dropped_uids)} used={res['n']}"
    )
    print_table(res)

    if args.tag:
        out = Path("outputs/metrics") / f"agreement_{args.tag}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(res, indent=2))
        print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
