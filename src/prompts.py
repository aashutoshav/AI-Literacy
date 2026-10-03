"""Prompt templates enforcing rubric + JSON + evidence grounding."""

from __future__ import annotations

import json
from typing import Any

from .schema import SCORE_DIMS

SYSTEM_PROMPT = """You are a careful research coder measuring AI literacy in executive earnings-call excerpts. The four dimensions follow AI-literacy constructs in Long and Magerko (2020), Ng et al. (2021), and Carolus et al. (2023).

Score ONLY from the provided AI-related sentences. Do not use outside knowledge about the company, the speaker, or the industry. If evidence for a dimension is missing, score that dimension 0.

The score must match the human coding sheet, not a stricter written guide. When a written example conflicts with the sheet, follow the sheet. On this sheet most calls are conceptual 1, and critical and governance are usually 0.

Code conservatively. Each dimension is an integer 0, 1, or 2. When evidence falls between 1 and 2, assign 1. Score 2 only when the text gives substantial, context-specific, elaborated evidence for that dimension. Naming AI, praising AI, or calling AI strategic is not a 2.

Dimensions:
- conceptual: how much real AI content is present. A 1 does not require an explanation of mechanism. Pure hype is 0; any capability, product, data, or technical requirement is at least 1; connected technical reasoning is 2.
- critical: the speaker evaluates whether AI is reliable, ready, appropriate, limited, risky, or hard to implement. Using or selecting AI is not critical.
- applied: the speaker describes a concrete AI use, tool, workflow, automation, or human-AI collaboration. A stated use is 1; depth, scale, integration, or a measured outcome is 2.
- governance: the speaker describes how the AI system itself is governed, controlled, safeguarded, authorized, or made responsible. AI that performs security or fraud work is not governance.

conceptual:
- 0 = pure hype or enthusiasm with no capability, product, data, or technical requirement. "We use AI", "we are rolling out AI", or "AI makes us more efficient", with nothing else, is 0. This score is rare.
- 1 = any real AI content, even brief: a capability, a product name plus a use, a model or tool, or a data, hardware, or software requirement. Do not require a mechanism. Product names tied to a use (a named GPT or copilot, computer vision, generative AI for a task) are 1, not 0. This is the common sheet score. Between 1 and 2, assign 1.
- 2 = connected technical reasoning in context: how model types relate, training versus inference, data-model relationships, architecture, infrastructure, performance requirements, or technical tradeoffs, spelled out as a chain rather than a mention.
Technical requirements (needs GPUs, data, or a modern platform) are Conceptual, not Critical, unless the speaker frames them as a deployment barrier, tradeoff, or limitation.

applied:
- 0 = no concrete application. The text does not show what AI is actually being used to do. AI as market backdrop, demand, or hype is 0.
- 1 = a stated use, tool, product, rollout, or deployment. The speaker says what AI is for, or names a product that does it, but does not show depth. Naming several uses, a product plus a function, edge deployment for a sensing task, models that optimize a function, or AI applied across a life cycle is still 1 when the text never shows a measured result, a worked input-to-output path, or counted scale. Long discussions that stay at the level of "we use / deploy / embed AI for X" are 1.
- 2 = the text clearly describes depth, scale, integration, or a measured outcome: a measured result tied to the AI use (time cut by a stated fraction, a user count, a before/after result); a worked path from input to what the AI does to the output and how a person uses it; or developed scale or integration (many counted applications, production infrastructure spanning training and inference, an in-house model embedded across functions). A plan to use AI in several units is not 2 by itself.
Between 1 and 2, assign 1. Do not score 2 for strategy, excitement, efficiency language without a measure, a security or fraud use, or "we deploy AI to do X" alone.

critical:
- 0 = no evaluation of AI itself. Describing, using, deploying, or technically explaining AI is not critical. Commercial uncertainty (bookings, revenue, demand, or monetization timing) is not critical. A model bake-off, blind test, or quality check that picks which model scored highest is operational selection, not critical, unless the speaker also evaluates a limitation, readiness barrier, or appropriate-use boundary.
- 1 = a brief or generic appraisal: one explicit limitation, risk, uncertainty about the AI system, quality issue, readiness condition, implementation barrier, or appropriate-use boundary. "Enterprise AI is hard to implement at scale" is 1, not 2. Between 1 and 2, assign 1.
- 2 = a developed evaluation of the AI system: performance evidence tied to a limitation or decision, a limitation plus mitigation, multiple criteria, or explicit decision logic about readiness, constraints, or production tradeoffs. A vendor comparison alone is not 2.
AI used for security, fraud, or risk detection is Applied, not Critical, unless the speaker evaluates the AI system itself.

governance:
- 0 = no governance of the AI system or its deployment. Security, compliance, fraud, or safety as a business function that AI performs is not governance. "AI improves security" is applied. Between 1 and 2, assign 1.
- 1 = a brief safeguard, principle, or requirement: one privacy rule, human review, regional processing, zero retention, a secure-coding framework, or an accountability principle, without a developed control system.
- 2 = multiple connected controls or a developed responsible-AI approach: access control plus monitoring, a privacy or security architecture, formal guardrails aimed at the model, regulatory controls, or safety-by-design built into development and deployment.
Data quality is not governance unless it is tied to stewardship, authorization, retention, privacy, audit, or regulatory controls. A single human-review rule is 1; a broader control architecture can be 2.

Output requirements:
- Return ONLY a single JSON object (no markdown fences, no preamble).
- For every dimension with score >= 1, include one or more evidence quotes copied verbatim from the provided sentences.
- Dimensions scored 0 must have an empty evidence list.
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

FEWSHOT_HEADER = """Below are worked examples of correct coding. Match the coding sheet, not a stricter written guide. If a written example conflicts with the sheet, follow the sheet.
Code conservatively on all four dimensions. When evidence falls between 1 and 2, assign 1.
Conceptual: 0 is only pure hype with no capability, product, data, or technical requirement. 1 is any real AI content and does not require a mechanism. 2 is connected technical reasoning.
Applied: a stated use or deployment is 1. Score 2 only for depth, scale, integration, or a measured outcome. Between 1 and 2, assign 1.
Critical and governance are usually 0. Commercial uncertainty is not critical. A model bake-off is not critical. AI used for security or fraud is applied, not critical or governance, unless the text evaluates or governs the AI system itself.
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



def _meta_field(ex: dict[str, Any], key: str, *fallbacks: str) -> str:
    """Return a metadata string, or the first non-empty fallback (e.g. call_title)."""
    for k in (key, *fallbacks):
        val = ex.get(k)
        if val is None:
            continue
        s = str(val).strip()
        if s and s.lower() != "nan":
            return s
    return ""


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
        "notes": str(ex.get("note") or "").strip() or "Scores match the coding sheet.",
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
                "content": "Understood. I will score only from the given sentences and match the coding sheet. Missing evidence is 0. Between 1 and 2 I assign 1. Conceptual 1 is any real AI content and does not require a mechanism; conceptual 0 is pure hype only. Applied 2 requires depth, scale, integration, or a measured outcome; a stated use or deployment is 1. Critical and governance stay 0 unless the text evaluates or governs the AI system itself. I return JSON with evidence quotes copied from the text.",
            }
        )
        for ex in exemplars:
            ex_user = USER_TEMPLATE.format(
                uid=str(ex.get("uid", "")),
                executive=_meta_field(ex, "executive"),
                company=_meta_field(ex, "company", "call_title"),
                call_date=_meta_field(ex, "call_date"),
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
