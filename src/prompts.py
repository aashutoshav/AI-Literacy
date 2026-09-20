"""Prompt templates enforcing rubric + JSON + evidence grounding."""

from __future__ import annotations

import json
from typing import Any

from .schema import SCORE_DIMS

SYSTEM_PROMPT = """You are a careful research coder measuring AI literacy in executive earnings-call excerpts.

Score ONLY from the provided AI-related sentences. Do not use outside knowledge about the company, CEO, or industry. If evidence is missing for a dimension, score 0.

Dimensions (integers 0, 1, or 2):
- conceptual: understanding of what AI/ML is or how it works at a high level.
- critical: awareness of risks, limits, ethics, uncertainty, or tradeoffs.
- applied: concrete use in products, operations, or decisions.
- governance: policies, oversight, compliance, accountability around AI.

Decision rules (summary):
- 0 = no evidence in the text for that dimension.
- 1 = partial / vague evidence.
- 2 = clear, specific evidence.

Important boundary for applied:
- applied=1 if AI use is mentioned at a high level (e.g. "we use AI in customer service") without operational detail.
- applied=2 only if the text names specific workflows, products, metrics, deployments, or decision processes.
Do NOT inflate applied to 2 just because AI is mentioned as useful or strategic.

Output requirements:
- Return ONLY a single JSON object (no markdown fences, no preamble).
- Include evidence quotes: for every dimension with score >= 1, quote one or more spans copied from the provided sentences that justify the score.
- Never invent facts or quotes that are not in the provided text.
"""

USER_TEMPLATE = """Code the following earnings-call AI-related sentences.

uid: {uid}
executive: {executive}
company: {company}
call_date: {call_date}

AI-related sentences:
{sentences}

Return JSON with this exact shape:
{{
  "uid": "{uid}",
  "scores": {{
    "conceptual": <0|1|2>,
    "critical": <0|1|2>,
    "applied": <0|1|2>,
    "governance": <0|1|2>
  }},
  "evidence": {{
    "conceptual": [<quote>, ...],
    "critical": [<quote>, ...],
    "applied": [<quote>, ...],
    "governance": [<quote>, ...]
  }},
  "notes": "<optional short rationale; no new facts>"
}}
"""

FEWSHOT_HEADER = """Below are worked examples of correct coding. Match this style and strictness, especially for applied 1 vs 2.
"""

CRITIQUE_SYSTEM = """You are auditing an AI-literacy coding JSON for schema fidelity and grounding.
Revise scores if evidence quotes are missing from the source text or do not support the score.
Return ONLY corrected JSON in the same schema. Do not invent new company facts."""

CRITIQUE_USER_TEMPLATE = """Source sentences:
{sentences}

Draft JSON:
{draft_json}

Return corrected JSON only.
"""


def _gold_assistant_json(ex: dict[str, Any]) -> str:
    scores = ex.get("scores") or {}
    evidence = {d: [] for d in SCORE_DIMS}
    # Prefer provided evidence; else empty (gold CSV may not have quotes)
    if isinstance(ex.get("evidence"), dict):
        for d in SCORE_DIMS:
            spans = ex["evidence"].get(d) or []
            evidence[d] = list(spans) if isinstance(spans, list) else []
    payload = {
        "uid": str(ex.get("uid", "")),
        "scores": {d: int(scores.get(d, 0)) for d in SCORE_DIMS},
        "evidence": evidence,
        "notes": "gold exemplar",
    }
    return json.dumps(payload, ensure_ascii=False)


def build_messages(
    *,
    uid: str,
    executive: str,
    company: str,
    call_date: str,
    sentences: str,
    exemplars: list[dict[str, Any]] | None = None,
) -> list[dict[str, str]]:
    """Build chat messages. If exemplars is non-empty, insert few-shot user/assistant pairs."""
    messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    if exemplars:
        messages.append({"role": "user", "content": FEWSHOT_HEADER})
        messages.append(
            {
                "role": "assistant",
                "content": "Understood. I will score only from the given sentences, keep applied=2 only for specific operational detail, and return JSON with evidence quotes.",
            }
        )
        for ex in exemplars:
            ex_user = USER_TEMPLATE.format(
                uid=str(ex.get("uid", "")),
                executive=str(ex.get("executive", "") or ""),
                company=str(ex.get("company", "") or ""),
                call_date=str(ex.get("call_date", "") or ""),
                sentences=str(ex.get("sentences", "") or ""),
            )
            messages.append({"role": "user", "content": ex_user})
            messages.append({"role": "assistant", "content": _gold_assistant_json(ex)})

    user = USER_TEMPLATE.format(
        uid=uid,
        executive=executive or "",
        company=company or "",
        call_date=call_date or "",
        sentences=sentences or "",
    )
    messages.append({"role": "user", "content": user})
    return messages


def build_critique_messages(*, sentences: str, draft_json: str) -> list[dict[str, str]]:
    return [
        {"role": "system", "content": CRITIQUE_SYSTEM},
        {
            "role": "user",
            "content": CRITIQUE_USER_TEMPLATE.format(
                sentences=sentences or "",
                draft_json=draft_json,
            ),
        },
    ]


__all__ = [
    "SYSTEM_PROMPT",
    "USER_TEMPLATE",
    "SCORE_DIMS",
    "build_messages",
    "build_critique_messages",
]
