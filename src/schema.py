"""Plain-dict schema for AI-literacy scores + evidence (no Pydantic)."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

SCORE_DIMS = ("conceptual", "critical", "applied", "governance")
VALID_SCORES = frozenset({0, 1, 2})

EMPTY_RESULT: dict[str, Any] = {
    "uid": "",
    "scores": {d: 0 for d in SCORE_DIMS},
    "evidence": {d: [] for d in SCORE_DIMS},
    "notes": "",
}


def blank_result(uid: str = "") -> dict[str, Any]:
    out = deepcopy(EMPTY_RESULT)
    out["uid"] = uid
    return out


def validate_result(obj: Any, *, require_evidence_for_nonzero: bool = True) -> list[str]:
    """Return a list of validation error strings (empty if OK)."""
    errors: list[str] = []
    if not isinstance(obj, dict):
        return ["result must be a dict"]

    if "uid" not in obj:
        errors.append("missing uid")

    scores = obj.get("scores")
    if not isinstance(scores, dict):
        errors.append("scores must be a dict")
        scores = {}

    evidence = obj.get("evidence")
    if not isinstance(evidence, dict):
        errors.append("evidence must be a dict")
        evidence = {}

    for dim in SCORE_DIMS:
        if dim not in scores:
            errors.append(f"missing scores.{dim}")
            continue
        val = scores[dim]
        if not isinstance(val, int) or isinstance(val, bool) or val not in VALID_SCORES:
            errors.append(f"scores.{dim} must be int in {{0,1,2}}, got {val!r}")
            continue
        spans = evidence.get(dim, [])
        if not isinstance(spans, list):
            errors.append(f"evidence.{dim} must be a list")
            continue
        if not all(isinstance(s, str) for s in spans):
            errors.append(f"evidence.{dim} must be list[str]")
            continue
        if require_evidence_for_nonzero and val >= 1 and len(spans) < 1:
            errors.append(f"scores.{dim}={val} requires >=1 evidence quote")
        if val == 0 and len(spans) > 0:
            # soft warning style: allow but flag
            errors.append(f"scores.{dim}=0 should have empty evidence (found {len(spans)})")

    return errors


def coerce_result(obj: dict[str, Any], uid: str | None = None) -> dict[str, Any]:
    """Clamp/fill a partially valid model output into schema shape."""
    out = blank_result(uid if uid is not None else str(obj.get("uid", "")))
    scores_in = obj.get("scores") if isinstance(obj.get("scores"), dict) else {}
    evid_in = obj.get("evidence") if isinstance(obj.get("evidence"), dict) else {}
    for dim in SCORE_DIMS:
        raw = scores_in.get(dim, 0)
        try:
            val = int(raw)
        except (TypeError, ValueError):
            val = 0
        out["scores"][dim] = val if val in VALID_SCORES else max(0, min(2, val))
        spans = evid_in.get(dim, [])
        if isinstance(spans, list):
            out["evidence"][dim] = [str(s) for s in spans if str(s).strip()]
        elif isinstance(spans, str) and spans.strip():
            out["evidence"][dim] = [spans.strip()]
    notes = obj.get("notes", "")
    out["notes"] = str(notes) if notes is not None else ""
    return out


# Human-labeled CSV uses "conceptual (0-2)" style headers.
GOLD_COL_ALIASES = {
    "conceptual": ("conceptual", "conceptual (0-2)", "conceptual (0-2)"),
    "critical": ("critical", "critical (0-2)", "critical (0-2)"),
    "applied": ("applied", "applied (0-2)", "applied (0-2)"),
    "governance": ("governance", "governance (0-2)", "governance (0-2)"),
}
TEXT_COL_CANDIDATES = ("AI-related sentences", "AI-related sentences", "text", "sentences")


def resolve_column(columns, candidates) -> str:
    cols = list(columns)
    for c in candidates:
        if c in cols:
            return c
    raise KeyError(f"None of {candidates} found in columns {cols}")


def normalize_gold_frame(df):
    """Rename gold score columns to short names; leave text column as-is."""
    import pandas as pd
    out = df.copy()
    rename = {}
    for short, aliases in GOLD_COL_ALIASES.items():
        if short in out.columns:
            continue
        for a in aliases:
            if a in out.columns:
                rename[a] = short
                break
    if rename:
        out = out.rename(columns=rename)
    return out
