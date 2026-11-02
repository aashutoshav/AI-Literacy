"""Prompt templates enforcing rubric + JSON + evidence grounding."""

from __future__ import annotations

import json
from typing import Any

from .schema import SCORE_DIMS

# The sheet-aligned system prompt is assembled from named sections so the
# per-dimension mode (perdim) can reuse one dimension's rubric verbatim.
# SYSTEM_PROMPT itself is unchanged, character for character.
_PREAMBLE = """You are a careful research coder measuring AI literacy in executive earnings-call excerpts. The four dimensions follow AI-literacy constructs in Long and Magerko (2020), Ng et al. (2021), and Carolus et al. (2023).

Score ONLY from the provided AI-related sentences. Do not use outside knowledge about the company, the speaker, or the industry. If evidence for a dimension is missing, score that dimension 0.

The score must match the human coding sheet, not a stricter written guide. When a written example conflicts with the sheet, follow the sheet. On this sheet most calls are conceptual 1, and critical and governance are usually 0.

Code conservatively. Each dimension is an integer 0, 1, or 2. When evidence falls between 1 and 2, assign 1. Score 2 only when the text gives substantial, context-specific, elaborated evidence for that dimension. Naming AI, praising AI, or calling AI strategic is not a 2.
"""

DIM_SUMMARY = {
    "conceptual": "- conceptual: how much real AI content is present. A 1 does not require an explanation of mechanism. Pure hype is 0; any capability, product, data, or technical requirement is at least 1; connected technical reasoning is 2.",
    "critical": "- critical: the speaker evaluates whether AI is reliable, ready, appropriate, limited, risky, or hard to implement. Using or selecting AI is not critical.",
    "applied": "- applied: the speaker describes a concrete AI use, tool, workflow, automation, or human-AI collaboration. A stated use is 1; depth, scale, integration, or a measured outcome is 2.",
    "governance": "- governance: the speaker describes how the AI system itself is governed, controlled, safeguarded, authorized, or made responsible. AI that performs security or fraud work is not governance.",
}

_TECH_REQ_NOTE = "Technical requirements (needs GPUs, data, or a modern platform) are Conceptual, not Critical, unless the speaker frames them as a deployment barrier, tradeoff, or limitation."

DIM_RUBRIC = {
    "conceptual": """conceptual:
- 0 = pure hype or enthusiasm with no capability, product, data, or technical requirement. "We use AI", "we are rolling out AI", or "AI makes us more efficient", with nothing else, is 0. This score is rare.
- 1 = any real AI content, even brief: a capability, a product name plus a use, a model or tool, or a data, hardware, or software requirement. Do not require a mechanism. Product names tied to a use (a named GPT or copilot, computer vision, generative AI for a task) are 1, not 0. This is the common sheet score. Between 1 and 2, assign 1.
- 2 = connected technical reasoning in context: how model types relate, training versus inference, data-model relationships, architecture, infrastructure, performance requirements, or technical tradeoffs, spelled out as a chain rather than a mention.
""" + _TECH_REQ_NOTE,
    "applied": """applied:
- 0 = no concrete application. The text does not show what AI is actually being used to do. AI as market backdrop, demand, or hype is 0.
- 1 = a stated use, tool, product, rollout, or deployment. The speaker says what AI is for, or names a product that does it, but does not show depth. Naming several uses, a product plus a function, edge deployment for a sensing task, models that optimize a function, or AI applied across a life cycle is still 1 when the text never shows a measured result, a worked input-to-output path, or counted scale. Long discussions that stay at the level of "we use / deploy / embed AI for X" are 1.
- 2 = the text clearly describes depth, scale, integration, or a measured outcome: a measured result tied to the AI use (time cut by a stated fraction, a user count, a before/after result); a worked path from input to what the AI does to the output and how a person uses it; or developed scale or integration (many counted applications, production infrastructure spanning training and inference, an in-house model embedded across functions). A plan to use AI in several units is not 2 by itself.
Between 1 and 2, assign 1. Do not score 2 for strategy, excitement, efficiency language without a measure, a security or fraud use, or "we deploy AI to do X" alone.""",
    "critical": """critical:
- 0 = no evaluation of AI itself. Describing, using, deploying, or technically explaining AI is not critical. Commercial uncertainty (bookings, revenue, demand, or monetization timing) is not critical. A model bake-off, blind test, or quality check that picks which model scored highest is operational selection, not critical, unless the speaker also evaluates a limitation, readiness barrier, or appropriate-use boundary.
- 1 = a brief or generic appraisal: one explicit limitation, risk, uncertainty about the AI system, quality issue, readiness condition, implementation barrier, or appropriate-use boundary. "Enterprise AI is hard to implement at scale" is 1, not 2. Between 1 and 2, assign 1.
- 2 = a developed evaluation of the AI system: performance evidence tied to a limitation or decision, a limitation plus mitigation, multiple criteria, or explicit decision logic about readiness, constraints, or production tradeoffs. A vendor comparison alone is not 2.
AI used for security, fraud, or risk detection is Applied, not Critical, unless the speaker evaluates the AI system itself.""",
    "governance": """governance:
- 0 = no governance of the AI system or its deployment. Security, compliance, fraud, or safety as a business function that AI performs is not governance. "AI improves security" is applied. Between 1 and 2, assign 1.
- 1 = a brief safeguard, principle, or requirement: one privacy rule, human review, regional processing, zero retention, a secure-coding framework, or an accountability principle, without a developed control system.
- 2 = multiple connected controls or a developed responsible-AI approach: access control plus monitoring, a privacy or security architecture, formal guardrails aimed at the model, regulatory controls, or safety-by-design built into development and deployment.
Data quality is not governance unless it is tied to stewardship, authorization, retention, privacy, audit, or regulatory controls. A single human-review rule is 1; a broader control architecture can be 2.""",
}

_OUTPUT_RULES = """Output requirements:
- Return ONLY a single JSON object (no markdown fences, no preamble).
- For every dimension with score >= 1, include one or more evidence quotes copied verbatim from the provided sentences.
- Dimensions scored 0 must have an empty evidence list.
- Never invent facts or quotes that are not in the provided text.
"""

SYSTEM_PROMPT = (
    _PREAMBLE
    + "\nDimensions:\n"
    + "\n".join(DIM_SUMMARY[d] for d in ("conceptual", "critical", "applied", "governance"))
    + "\n\n"
    + "\n\n".join(DIM_RUBRIC[d] for d in ("conceptual", "applied", "critical", "governance"))
    + "\n\n"
    + _OUTPUT_RULES
)

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



# ---------------------------------------------------------------------------
# Prompt v3 ("fix3"), behind --prompt-version v3. Built from the miss analysis in
# outputs/analysis/misses_sheetalign_12b_zeroshot.md. SYSTEM_PROMPT (sheet-aligned)
# above is left untouched so earlier runs stay comparable.
# ---------------------------------------------------------------------------

DIM_SUMMARY_V3 = {
    "conceptual": DIM_SUMMARY["conceptual"],
    "critical": "- critical: the speaker evaluates AI itself: its limits, risks, accuracy, reliability, readiness, cost-effectiveness, or barriers to making it work. Using, selecting, or describing AI is not critical.",
    "applied": "- applied: the speaker describes a concrete AI use, tool, workflow, automation, or human-AI collaboration. A use in one area is 1; use across several functions or business units, or a measured outcome, scale, or integration, is 2.",
    "governance": "- governance: the speaker discusses security, privacy, fraud, risk, compliance, access control, human review, or oversight in relation to AI or its deployment.",
}

DIM_RUBRIC_V3 = {
    "conceptual": DIM_RUBRIC["conceptual"].replace(
        "spelled out as a chain rather than a mention.",
        "spelled out as a chain rather than a mention. A connected explanation of how a model or system works, or of its capabilities described in some depth, is also 2.",
    ),
    "applied": """applied:
- 0 = no concrete application. The text does not show what AI is actually being used to do. AI as market backdrop, demand, or hype is 0.
- 1 = a concrete AI use, tool, product, or deployment in one area, without a measured outcome, counted scale, or integration across functions.
- 2 = AI deployed or applied across several functions, business units, products, or processes (for example content creation, translation, and back-office processes in the same company); or a measured outcome tied to the AI use (time cut by a stated fraction, a user count, a before/after result); or developed scale or integration (production infrastructure, an in-house model embedded across functions, a worked path from input to AI output to how a person uses it). Plans to apply AI across several business units count as 2.
Use "between 1 and 2, assign 1" only when it is genuinely unclear whether the use goes beyond one area.""",
    "critical": """critical:
- 0 = no evaluation of AI itself. Describing, using, deploying, selecting, or technically explaining AI is not critical. Commercial uncertainty (bookings, revenue, demand, or monetization timing) is not critical. Prerequisites stated neutrally (AI needs good data, data quality, infrastructure, compute, connections to other systems, or a modern platform) are 0, and so are timing remarks such as "it's early days" or "still early", unless the speaker frames them as a limitation, risk, or barrier of AI itself.
- 1 = a real concern about AI: an explicit limitation, risk, accuracy or quality problem, doubt about cost-effectiveness or return, readiness condition, implementation barrier, or appropriate-use boundary. One such remark is enough for 1. "Getting AI to work in an enterprise at scale is really hard" is 1.
- 2 = a sustained or elaborated appraisal of AI: the speaker works through whether AI delivers, with evidence or criteria, a limitation plus mitigation, several connected concerns, or explicit decision logic about readiness, constraints, or tradeoffs.
Read long calls all the way through: critical remarks are often one or two sentences inside a long discussion of uses.""",
    "governance": """governance:
- 0 = no security, privacy, fraud, risk, compliance, access-control, human-review, or oversight content connected to AI. A passing word with no substance stays 0: "built to satisfy enterprise governance requirements", "tools inside our firewall", or "we control" how much goes to a model, with nothing about what the control is.
- 1 = a brief mention of such a control or concern in relation to AI or AI deployment: AI used for security, fraud detection, risk, or compliance work; access policies; one privacy or data-use rule; a human-in-the-loop review; regional processing; or an accountability principle.
- 2 = elaborated policy, oversight, or controls around AI: several connected controls, securing AI systems or AI agents themselves (privilege controls, defenses against prompt injection or data leakage), a security or privacy architecture, formal guardrails, regulatory controls, or a developed responsible-AI approach.
Between 1 and 2, assign 1.""",
}

_PREAMBLE_V3 = _PREAMBLE.replace(
    "On this sheet most calls are conceptual 1, and critical and governance are usually 0.",
    "On this sheet most calls are conceptual 1; critical and governance are 0 on most calls, but about three in ten calls score at least 1 on each.",
)

SYSTEM_PROMPT_V3 = (
    _PREAMBLE_V3
    + "\nDimensions:\n"
    + "\n".join(DIM_SUMMARY_V3[d] for d in ("conceptual", "critical", "applied", "governance"))
    + "\n\n"
    + "\n\n".join(DIM_RUBRIC_V3[d] for d in ("conceptual", "applied", "critical", "governance"))
    + "\n\n"
    + _OUTPUT_RULES
)

FEWSHOT_HEADER_V3 = """Below are worked examples of correct coding. Match the human coding sheet.
Conceptual: 1 is any real AI content; 2 is connected technical reasoning or an in-depth account of how a system works.
Applied: one concrete use is 1; use across several functions, or a measured outcome, scale, or integration, is 2.
Critical: neutral prerequisites and "early days" are 0; a real concern about AI's limits, risks, accuracy, cost-effectiveness, or barriers is 1; an elaborated appraisal is 2.
Governance: security, privacy, fraud, risk, compliance, access control, or human review connected to AI is at least 1; a passing word with no substance is 0; elaborated controls around AI are 2.
"""


# ---------------------------------------------------------------------------
# Prompt v4 ("fix4"), behind --prompt-version v4: identical to v3 except the
# applied dimension, which uses the sheet-aligned (baseline) applied wording.
# ---------------------------------------------------------------------------

DIM_SUMMARY_V4 = {**DIM_SUMMARY_V3, "applied": DIM_SUMMARY["applied"]}
DIM_RUBRIC_V4 = {**DIM_RUBRIC_V3, "applied": DIM_RUBRIC["applied"]}

SYSTEM_PROMPT_V4 = (
    _PREAMBLE_V3
    + "\nDimensions:\n"
    + "\n".join(DIM_SUMMARY_V4[d] for d in ("conceptual", "critical", "applied", "governance"))
    + "\n\n"
    + "\n\n".join(DIM_RUBRIC_V4[d] for d in ("conceptual", "applied", "critical", "governance"))
    + "\n\n"
    + _OUTPUT_RULES
)

FEWSHOT_HEADER_V4 = FEWSHOT_HEADER_V3.replace(
    "Applied: one concrete use is 1; use across several functions, or a measured outcome, scale, or integration, is 2.",
    "Applied: a stated use or deployment is 1. Score 2 only for depth, scale, integration, or a measured outcome. Between 1 and 2, assign 1.",
)

# ---------------------------------------------------------------------------
# Prompt v5 ("fix5"), behind --prompt-version v5. Starts from v4 and revises the
# conceptual and applied 1-vs-2 rules, the conceptual and applied 0-vs-1 rules, the
# critical and governance thresholds, and the base-rate note, from the DEV-split miss
# analysis of both coding sets (outputs/analysis/misses_n200_dev.md). Base rates are
# the pooled DEV distribution (170 calls). v3 and v4 are unchanged.
# ---------------------------------------------------------------------------

_PREAMBLE_V5 = """You are a careful research coder measuring AI literacy in executive earnings-call excerpts. The four dimensions follow AI-literacy constructs in Long and Magerko (2020), Ng et al. (2021), and Carolus et al. (2023).

Score ONLY from the provided AI-related sentences. Do not use outside knowledge about the company, the speaker, or the industry. If evidence for a dimension is missing, score that dimension 0.

The score must match the human coding sheet, not a stricter written guide. Typical sheet distribution (% of calls at 0 / 1 / 2): conceptual about 7 / 59 / 34; applied about 12 / 54 / 34; critical about 72 / 24 / 4; governance about 80 / 16 / 4. So a 2 on conceptual or applied is common (about one call in three), while critical and governance are 0 on most calls.

Score what the text shows. Each dimension is an integer 0, 1, or 2. Excerpts range from one or two sentences to dozens: a short excerpt with one brief AI mention rarely supports more than 1, while an excerpt that develops AI content over several specific statements often earns 2 on conceptual and applied. Do not default to 1 when the text clearly develops a dimension. Naming AI, praising AI, or calling AI strategic is not a 2 on its own; repeated generic claims are not development.
"""

DIM_SUMMARY_V5 = {
    "conceptual": "- conceptual: how much real, specific AI content is present: what AI systems are, do, or need. A bare mention or label is 0; brief real AI content is 1; specific AI content explained or developed over several statements is 2.",
    "critical": "- critical: the text raises a limitation, risk, threat, accuracy problem, uncertainty, or barrier connected to AI. Using, selecting, or praising AI is not critical.",
    "applied": "- applied: what AI is actually used for, or the AI product or service the company offers. A brief stated use or offering is 1; several concrete uses with what AI does in each, a measured outcome, a worked path, or deployment at scale is 2.",
    "governance": DIM_SUMMARY_V3["governance"],
}

DIM_RUBRIC_V5 = {
    "conceptual": """conceptual:
- 0 = AI is only named: inside an analyst question with no answer about AI, as a passing buzzword, or as a label with nothing said about what the AI is, does, or needs. This score is uncommon.
- 1 = brief real AI content: a capability, product, model, tool, or data or hardware requirement, mentioned without explanation; AI described as a market driver or source of demand ("demand from AI data centers is driving our sales"); or a short list of AI product names. Most one- to three-sentence excerpts are 1.
- 2 = specific AI content explained or developed across several statements. Any of these is enough: what particular AI systems do, described concretely (inputs, outputs, tasks) for more than one capability; how a model or system works, or distinctions among model types (small versus large models, training versus inference, in-house versus external models, generative versus predictive); or AI's technical requirements together with why they arise (more GPUs raise power use, which needs more capacitors or larger batteries; data must be cleaned before models are reliable). A long excerpt that keeps returning to specific AI capabilities or requirements is 2 even without a mechanism.
""" + _TECH_REQ_NOTE,
    "applied": """applied:
- 0 = no use or offering of AI by the company, its customers, or partners: AI appears only as a general trend, an analyst question, or hype.
- 1 = a stated use, tool, product, rollout, or plan, without detail: "we use AI in our workflows", one named AI product with its function, or the company building, selling, or financing products or capacity for AI (chips, components, power, data-center space). Supplying AI demand counts as 1, not 0.
- 2 = the text shows AI in concrete use in at least one of these ways: two or more distinct uses, each with what the AI does in it (drafting credit memos and pricing loans; summarising calls and answering agents' questions); a measured outcome tied to the AI use (time cut by a stated share, a count of users, interactions, or members, a before-and-after result); a worked path from input to AI output to how people use it; or deployment at scale or integrated across functions or products, described specifically. A bare list of product names, or "AI across the business" with no specific use, stays 1.""",
    "critical": """critical:
- 0 = no limitation, risk, threat, or concern connected to AI. Describing, using, deploying, selecting, or praising AI is not critical. Commercial uncertainty about revenue or demand timing is not critical. Prerequisites stated neutrally (AI needs data, compute, or a modern platform) and timing remarks such as "it's early days" stay 0 unless framed as a limitation, risk, or barrier.
- 1 = at least one explicit remark that AI carries a risk, threat, limitation, accuracy or reliability problem, cost or return doubt, readiness barrier, or appropriate-use boundary. This includes AI-enabled threats (attackers or fraudsters using AI), AI disruption risk to the business, a statement that human judgment must stay in control because AI is not enough, and a remark that AI's quality depends on data or algorithms. One such remark is enough. Read long excerpts all the way through: critical remarks are often one sentence inside a long discussion of uses.
- 2 = a sustained or elaborated appraisal: the speaker works through whether AI delivers, with evidence or criteria, a limitation plus mitigation, several connected concerns, or explicit decision logic about readiness, constraints, or tradeoffs.""",
    "governance": DIM_RUBRIC_V3["governance"].replace(
        "- 1 = a brief mention of such a control or concern in relation to AI or AI deployment:",
        "- 1 = a brief mention of such a control or concern in relation to AI or AI deployment, including an AI product or service whose purpose is security, safety, fraud prevention, or compliance:",
    ),
}

SYSTEM_PROMPT_V5 = (
    _PREAMBLE_V5
    + "\nDimensions:\n"
    + "\n".join(DIM_SUMMARY_V5[d] for d in ("conceptual", "critical", "applied", "governance"))
    + "\n\n"
    + "\n\n".join(DIM_RUBRIC_V5[d] for d in ("conceptual", "applied", "critical", "governance"))
    + "\n\n"
    + _OUTPUT_RULES
)

FEWSHOT_HEADER_V5 = """Below are worked examples of correct coding. Match the human coding sheet.
Conceptual: a bare mention is 0; brief real AI content is 1; specific AI content explained or developed over several statements (what systems do, how they work, technical requirements and why) is 2.
Applied: a brief stated use or AI offering, including supplying products for AI, is 1; several concrete uses with what AI does in each, a measured outcome, a worked path, or specific deployment at scale is 2.
Critical: one explicit risk, threat, limitation, or accuracy concern connected to AI is 1; an elaborated appraisal is 2; neutral prerequisites and "early days" are 0.
Governance: security, privacy, fraud, risk, compliance, access control, or human review connected to AI is at least 1; a passing word with no substance is 0; elaborated controls around AI are 2.
"""

PROMPT_VERSIONS = ("sheet", "v3", "v4", "v5")


def system_prompt_for(version: str = "sheet") -> str:
    if version == "v3":
        return SYSTEM_PROMPT_V3
    if version == "v4":
        return SYSTEM_PROMPT_V4
    if version == "v5":
        return SYSTEM_PROMPT_V5
    return SYSTEM_PROMPT


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
    prompt_version: str = "sheet",
) -> list[dict[str, str]]:
    """Build chat messages. If exemplars is non-empty, insert few-shot user/assistant pairs."""
    messages: list[dict[str, str]] = [{"role": "system", "content": system_prompt_for(prompt_version)}]

    if exemplars:
        messages.append({"role": "user", "content": {"v3": FEWSHOT_HEADER_V3, "v4": FEWSHOT_HEADER_V4, "v5": FEWSHOT_HEADER_V5}.get(prompt_version, FEWSHOT_HEADER)})
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



# ---------------------------------------------------------------------------
# Per-dimension mode (perdim): one prompt per dimension, same preamble and
# grounding rules, only that dimension's rubric section.
# ---------------------------------------------------------------------------

_PERDIM_OUTPUT_RULES = """Output requirements:
- Return ONLY a single JSON object (no markdown fences, no preamble).
- If the score is >= 1, include one or more evidence quotes copied verbatim from the provided sentences.
- If the score is 0, the evidence list must be empty.
- Never invent facts or quotes that are not in the provided text.
"""

PERDIM_USER_TEMPLATE = """Code ONLY the {dim} dimension for the following earnings-call AI-related sentences.

uid: {uid}
executive: {executive}
company: {company}
call_date: {call_date}

AI-related sentences:
{sentences}

Return JSON with this exact shape:
{{
  "uid": "{uid}",
  "dimension": "{dim}",
  "score": <0|1|2>,
  "evidence": [<quote>, ...],
  "notes": "<optional short rationale; no new facts>"
}}
"""


def perdim_system_prompt(dim: str, prompt_version: str = "sheet") -> str:
    if dim not in DIM_RUBRIC:
        raise KeyError(f"unknown dimension {dim!r}")
    v3 = prompt_version in ("v3", "v4", "v5")
    summ = {"v3": DIM_SUMMARY_V3, "v4": DIM_SUMMARY_V4, "v5": DIM_SUMMARY_V5}.get(prompt_version, DIM_SUMMARY)
    rubr = {"v3": DIM_RUBRIC_V3, "v4": DIM_RUBRIC_V4, "v5": DIM_RUBRIC_V5}.get(prompt_version, DIM_RUBRIC)
    parts = [
        {"v5": _PREAMBLE_V5}.get(prompt_version, _PREAMBLE_V3 if v3 else _PREAMBLE),
        f"\nYou are scoring ONE dimension only: {dim}. Ignore the other AI-literacy dimensions.\n",
        summ[dim],
        "",
        rubr[dim],
    ]
    if dim == "critical" and not v3:
        # Boundary note that lives in the conceptual section of the full prompt.
        parts.append(_TECH_REQ_NOTE)
    parts += ["", _PERDIM_OUTPUT_RULES]
    return "\n".join(parts)


def build_perdim_messages(
    *,
    dim: str,
    uid: str,
    executive: str,
    company: str,
    call_date: str,
    sentences: str,
    prompt_version: str = "sheet",
) -> list[dict[str, str]]:
    user = PERDIM_USER_TEMPLATE.format(
        dim=dim,
        uid=uid,
        executive=executive or "",
        company=company or "",
        call_date=call_date or "",
        sentences=sentences or "",
    )
    return [
        {"role": "system", "content": perdim_system_prompt(dim, prompt_version)},
        {"role": "user", "content": user},
    ]


__all__ = [
    "SYSTEM_PROMPT",
    "USER_TEMPLATE",
    "SCORE_DIMS",
    "build_messages",
    "build_critique_messages",
    "build_perdim_messages",
    "perdim_system_prompt",
    "DIM_RUBRIC",
    "SYSTEM_PROMPT_V3",
    "SYSTEM_PROMPT_V4",
    "system_prompt_for",
]
