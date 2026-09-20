"""Agreement metrics vs human AI-literacy labels."""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np

from .schema import SCORE_DIMS

try:
    from sklearn.metrics import cohen_kappa_score, confusion_matrix
except ImportError:  # pragma: no cover
    cohen_kappa_score = None  # type: ignore
    confusion_matrix = None  # type: ignore


def _as_int_array(y: Sequence | Iterable) -> np.ndarray:
    return np.asarray(list(y), dtype=int)


def exact_match(y_true: Sequence, y_pred: Sequence) -> float:
    yt, yp = _as_int_array(y_true), _as_int_array(y_pred)
    if len(yt) == 0:
        return float("nan")
    return float(np.mean(yt == yp))


def adjacent_accuracy(y_true: Sequence, y_pred: Sequence, max_dist: int = 1) -> float:
    yt, yp = _as_int_array(y_true), _as_int_array(y_pred)
    if len(yt) == 0:
        return float("nan")
    return float(np.mean(np.abs(yt - yp) <= max_dist))


def quadratic_weighted_kappa(y_true: Sequence, y_pred: Sequence) -> float:
    """Cohen's kappa with quadratic weights (ordinal 0–2)."""
    yt, yp = _as_int_array(y_true), _as_int_array(y_pred)
    if len(yt) == 0:
        return float("nan")
    if cohen_kappa_score is None:
        raise ImportError("scikit-learn is required for quadratic_weighted_kappa")
    return float(cohen_kappa_score(yt, yp, weights="quadratic", labels=[0, 1, 2]))


def joint_exact_match(df_true_scores: dict[str, Sequence], df_pred_scores: dict[str, Sequence]) -> float:
    """Fraction of rows where all four dimensions match exactly."""
    mats = []
    for dim in SCORE_DIMS:
        mats.append(_as_int_array(df_true_scores[dim]) == _as_int_array(df_pred_scores[dim]))
    if not mats:
        return float("nan")
    return float(np.mean(np.logical_and.reduce(mats)))


def per_dimension_report(y_true: Sequence, y_pred: Sequence) -> dict:
    yt, yp = _as_int_array(y_true), _as_int_array(y_pred)
    report = {
        "n": int(len(yt)),
        "exact_match": exact_match(yt, yp),
        "adjacent_accuracy": adjacent_accuracy(yt, yp),
    }
    try:
        report["quadratic_weighted_kappa"] = quadratic_weighted_kappa(yt, yp)
    except Exception as exc:  # noqa: BLE001
        report["quadratic_weighted_kappa"] = None
        report["kappa_error"] = str(exc)
    if confusion_matrix is not None and len(yt):
        report["confusion_matrix"] = confusion_matrix(yt, yp, labels=[0, 1, 2]).tolist()
    return report


def full_report(y_true_by_dim: dict[str, Sequence], y_pred_by_dim: dict[str, Sequence]) -> dict:
    out: dict = {"dimensions": {}, "joint_exact_match": None}
    for dim in SCORE_DIMS:
        if dim not in y_true_by_dim or dim not in y_pred_by_dim:
            continue
        out["dimensions"][dim] = per_dimension_report(y_true_by_dim[dim], y_pred_by_dim[dim])
    try:
        out["joint_exact_match"] = joint_exact_match(y_true_by_dim, y_pred_by_dim)
    except Exception as exc:  # noqa: BLE001
        out["joint_exact_match_error"] = str(exc)
    return out


def krippendorff_alpha_ordinal_stub(*_args, **_kwargs) -> float:
    """Placeholder: install `krippendorff` later for ordinal alpha on multi-coder designs."""
    raise NotImplementedError(
        "Krippendorff's alpha not bundled; use quadratic weighted kappa for v0, "
        "or add the krippendorff package for ordinal alpha."
    )
