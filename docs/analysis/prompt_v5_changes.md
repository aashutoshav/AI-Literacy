# Prompt v5 (`--prompt-version v5`, tag `fix5`): changes from v4

v5 is v4 with the edits below. The sheet-aligned, v3 and v4 prompts are unchanged; a check confirmed their full and per-dimension prompts are identical before and after the edit. Every rule comes from the DEV halves of both coding sets (`outputs/analysis/misses_n200_dev.md`). The rules contain no call IDs and no copied call text.

| Part | v4 | v5 |
|---|---|---|
| Preamble, base rates | "most calls are conceptual 1; critical and governance are 0 on most calls, but about three in ten calls score at least 1 on each" | Pooled DEV distribution stated per dimension: conceptual about 7/59/34, applied 12/54/34, critical 72/24/4, governance 80/16/4. A 2 on conceptual or applied is common. |
| Preamble, default | "Code conservatively … When evidence falls between 1 and 2, assign 1." | "Score what the text shows." Short excerpts rarely exceed 1; excerpts that develop AI content over several specific statements often earn 2 on conceptual and applied. Do not default to 1 when the text clearly develops a dimension. |
| Conceptual 0 | Pure hype with no capability, product, data or requirement (AI as market backdrop treated as hype) | AI only named: in an unanswered analyst question, as a buzzword, or as a bare label. Uncommon. |
| Conceptual 1 | Any real AI content; "the common sheet score. Between 1 and 2, assign 1." | Brief real AI content, including AI as a market driver or demand, and short lists of AI products. Most 1–3 sentence excerpts. |
| Conceptual 2 | Connected technical reasoning spelled out as a chain (v3/v4 add: in-depth account of how a system works) | Specific AI content explained or developed across several statements: what particular systems do (more than one capability), how a system works or distinctions among model types, or technical requirements with why they arise. A long excerpt that keeps returning to specific capabilities or requirements is 2 even without a mechanism. |
| Applied 0 | No concrete application; AI as market backdrop, demand or hype is 0 | No use or offering of AI by the company, its customers or partners: only a general trend, a question, or hype. |
| Applied 1 | A stated use, tool, product or rollout without depth | Same, plus: the company building, selling or financing products or capacity for AI counts as 1, not 0. |
| Applied 2 | Depth, scale, integration or a measured outcome; "between 1 and 2, assign 1" | Any of: two or more distinct uses, each with what AI does; a measured outcome; a worked input-to-output path; or specific deployment at scale or across functions. A bare list of product names or "AI across the business" stays 1. (Between v4 and v3; v3 made any multi-area mention 2.) |
| Critical 1 | One explicit limitation, risk, accuracy problem, cost doubt, barrier or boundary | Same, plus: AI-enabled threats (attackers or fraud using AI), AI disruption risk, human judgment kept because AI is not enough, and AI quality depending on data or algorithms. Neutral prerequisites and "early days" still 0. |
| Critical 2 | Sustained or elaborated appraisal | Unchanged in substance. |
| Governance | v3/v4 rule | Unchanged, except level 1 adds "an AI product or service whose purpose is security, safety, fraud prevention, or compliance". |
| Few-shot header | v4 header | New v5 header summarising the above. |

New few-shot exemplars: `configs/fewshot_exemplars_n200dev.json`, 10 DEV calls from the 200 set:
- S2-0016: conceptual 2, applied 2.
- S2-0065: conceptual 2 from requirements, applied 1 from supplying AI demand.
- S2-0066: a short product list, 1/1.
- S2-0009: applied 2 with conceptual 1.
- S2-0113: AI as a market trend, conceptual 1, applied 0.
- S2-0006: supplying AI demand, applied 1.
- S2-0012: one risk remark, critical 1.
- S2-0038: AI for safety, governance 1.
- S2-0070: governance 2, critical 1.
- S3-0023: "AI" meaning avian influenza, all 0.

Known tension: the 143 set codes several multi-use, mid-length excerpts as conceptual 1 and applied 1 that the 200 set would code 2. v5's conceptual and applied 2 rules follow the 200 set and the pooled DEV rates, so v5 may lose agreement on those 143-set calls.
