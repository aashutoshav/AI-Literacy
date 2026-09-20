# Grounding & schema fidelity for LLM AI-literacy coding

**Status:** Draft rubrics — refine with PIs before locking the codebook.

This document describes how we keep Gemma 4 coding **grounded** in the provided earnings-call sentences (no invented company facts) and aligned to the human 0–2 scheme in `coding.csv`.

## Dimensions (draft definitions)

Scores apply **only** to the supplied `AI-related sentences` for that row. Absence of evidence → score **0** for that dimension (do not infer from company reputation).

### Conceptual (0–2) — understanding of what AI is / how it works at a high level

| Score | Decision rule |
|-------|----------------|
| **0** | No conceptual framing of AI/ML (only buzzword use, or AI mentioned without explaining capability/nature). |
| **1** | Mentions AI concepts at a basic level (e.g., “machine learning,” “automation,” “models”) without linking mechanisms to business logic. |
| **2** | Clear conceptual literacy: distinguishes AI capabilities/limits, data/model role, or compares AI to prior tech in a substantive way. |

### Critical (0–2) — awareness of risks, limits, ethics, uncertainty

| Score | Decision rule |
|-------|----------------|
| **0** | No critical stance; purely promotional or neutral mention without risks/limits. |
| **1** | Light acknowledgment of challenges, uncertainty, or “still early” without specifics. |
| **2** | Explicit critical literacy: risks (bias, safety, reliability), limitations, regulatory/ethical tension, or tradeoffs tied to AI use. |

### Applied (0–2) — concrete use in products, ops, or decisions

| Score | Decision rule |
|-------|----------------|
| **0** | No concrete application described (aspirational only / vague “exploring AI”). |
| **1** | Mentions a use area (e.g., “in customer service”) without operational detail. |
| **2** | Specific applied literacy: named workflows, products, metrics, deployments, or decision processes using AI. |

### Governance (0–2) — policies, oversight, compliance, accountability around AI

| Score | Decision rule |
|-------|----------------|
| **0** | No governance language. |
| **1** | Vague controls (“responsible AI,” “guidelines”) without owners/processes. |
| **2** | Concrete governance: boards/committees, policies, audits, compliance programs, human oversight, risk frameworks tied to AI. |

Literature alignment (high level): dimensions echo common AI-literacy facets — *knowing*, *critically evaluating*, *using/applying*, and *governing/responsible use*. Treat labels as **research codebook drafts**.

## Structured JSON-only output

The model must return **only** a JSON object (no markdown fences in production prompts if the parser is strict):

```json
{
  "uid": "<string>",
  "scores": {
    "conceptual": 0,
    "critical": 0,
    "applied": 0,
    "governance": 0
  },
  "evidence": {
    "conceptual": ["quoted span justifying score"],
    "critical": [],
    "applied": ["..."],
    "governance": []
  },
  "notes": "optional short rationale; no new facts"
}
```

Rules:

- Scores ∈ {0, 1, 2} integers.
- **Forced evidence:** each dimension with score ≥ 1 must include ≥ 1 verbatim (or near-verbatim) quote from the provided sentences.
- Empty evidence arrays only when score is 0.
- **Refusal to invent:** if text is insufficient, score 0; never use outside knowledge about the company or CEO.

## Few-shot exemplars

> **Important:** Prefer exemplars drawn from `coding.csv`. Below are **illustrative anonymized drafts** for prompt engineering until replaced by a scripted sample of 4–6 diverse gold rows (run on the Mac after scaffolding). Do not treat company names below as real labels from the CSV.

### Exemplar A — high applied, low critical/governance (illustrative)

- **Text (short):** “• We embedded generative AI into our support chatbot, cutting handle time 18%. • Model outputs are reviewed by agents before customer send.”
- **Gold (illustrative):** conceptual=1, critical=0, applied=2, governance=1

### Exemplar B — conceptual + critical (illustrative)

- **Text:** “• AI is not magic; it is statistical pattern recognition on our historical claims data. • Hallucinations remain a risk, so we gate recommendations behind actuarial review.”
- **Gold:** conceptual=2, critical=2, applied=1, governance=1

### Exemplar C — buzzword-only (illustrative)

- **Text:** “• We are excited about the AI opportunity across the enterprise.”
- **Gold:** conceptual=0, critical=0, applied=0, governance=0

### Exemplar D — governance-forward (illustrative)

- **Text:** “• Our AI risk committee reports quarterly to the board. • We adopted an internal AI use policy covering vendor models and data retention.”
- **Gold:** conceptual=1, critical=1, applied=0, governance=2

### Exemplar E — applied product detail (illustrative)

- **Text:** “• Computer vision models now inspect 100% of line items on Line 4. • Defect escape rate fell 30% versus the prior optical system.”
- **Gold:** conceptual=1, critical=0, applied=2, governance=0

### Exemplar F — mixed, moderate (illustrative)

- **Text:** “• We use ML demand forecasts in planning. • Results vary by region; we are still learning where the models underperform.”
- **Gold:** conceptual=1, critical=1, applied=2, governance=0

**TODO:** Replace A–F with anonymized excerpts + gold scores from real `coding.csv` rows (diverse score profiles). Helper:

```bash
python3 - <<'PY'
import pandas as pd
df = pd.read_csv("coding.csv")
# diversify by score tuple
df["sig"] = df[["conceptual","critical","applied","governance"]].astype(str).agg("-".join, axis=1)
print(df.groupby("sig").size().sort_values(ascending=False).head(20))
print(df.sample(6, random_state=42)[
  ["uid","company","conceptual","critical","applied","governance","AI-related sentences"]
].to_string())
PY
```

## Calibration / validation

Hold out human labels; compare model preds on the same `uid`s:

| Metric | Purpose |
|--------|---------|
| Exact-match accuracy (per dim + joint) | Strict agreement |
| Adjacent agreement (|pred−gold| ≤ 1) | Ordinal near-misses |
| Quadratic weighted Cohen’s κ | Ordinal agreement beyond chance |
| Krippendorff’s α (ordinal) | Multi-coder style reliability (optional; implement via custom or `krippendorff` pkg later) |

Implementation lives in `src/metrics.py` and `src/validate.py`.

## Optional dual-pass

1. **Score pass:** JSON scores + evidence quotes.  
2. **Critique pass:** given text + draft JSON, check evidence spans are present in text and scores follow rubric; revise if needed.

Enable later via CLI flag; not required for v0.

## CEO gender (missing in CSV)

`coding.csv` has **no CEO gender** field. Female vs male CEO analysis needs a separate join table, e.g. `data/ceo_gender.csv` with keys `(company, executive, call_date)` or `uid` → `{female|male|unknown}`. Keep that file out of git if sensitive (see `.gitignore`).

## Prompt enforcement

See `src/prompts.py`: system rubric + user payload with sentences + JSON schema reminder + evidence requirement.
