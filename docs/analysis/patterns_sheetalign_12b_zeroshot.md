## Patterns (read from the tables below)

All counts are from the 143 calls in `data/coding.csv` against `outputs/preds_zeroshot_12b_n143.csv` (sheet-aligned 12B zero-shot, job 6052529). Keyword counts are plain substring matches on the AI sentences, so they show where a pattern sits, not why the coders chose a score.

**Governance (36 disagreements; model lower on 30).**
- The model under-calls governance. The human codes have 43 calls at governance 1 or 2; the model gives 1 or 2 on 22, and only 17 of those overlap. 25 of the 37 human governance 1 calls were scored 0.
- Security-related AI content is the main gap. 23 calls contain "secur"; the human codes give governance 1 or 2 on 20 of them, the model on 8. Of the 25 governance 1 calls the model scored 0, 16 mention security, fraud, risk, or compliance (e.g. TR034 Okta AI access-policy recommender, TR220 lidar perception sold for perimeter security, TR106 AI fraud detection, TR107 AI in risk and compliance functions). The current prompt tells the model the opposite ("AI that performs security or fraud work is not governance"), so on this point the prompt does not match the human codes.
- Governance 1 and 2 are more common in longer calls (mean 14.9 and 26.5 AI sentences vs 9.4 for governance 0). Several human governance 1 calls show no obvious control language in the text (e.g. TR061, TR039, TR108), so some of these misses cannot be explained from the excerpt alone.
- The 5 over-calls (human 0, model 1) are passing mentions the model read as safeguards: "built to satisfy enterprise governance requirements" (TR005), a data-use commitment (TR017), tools "inside of our firewall" (TR071), an "in-house AI quality tool" (TR103), and "we control" LLM volume (TR125).
- Governance 2 is rare (6 calls) and the model got 1 of them; 4 were scored 1 and 1 (TR006, securing AI agents with privilege controls) was scored 0.

**Critical (33 disagreements; 16 higher, 17 lower).**
- The model's number of critical 1/2 calls is about right (45 vs 42 in the human codes) but they land on different calls: 16 of the model's 45 are human 0, and it misses 13 of the 42 human 1/2 calls.
- Over-calls are mostly prerequisite or timing language the human codes leave at 0: "what you also need is high data quality" (TR007), "direct connections ... are necessary" (TR044), "you need a modern and flexible infrastructure" (TR107), "requires more than just gen AI tech" (TR193), "it's early days" (TR038, TR045, TR049), inference cost (TR092).
- Under-calls: 12 human critical 1 calls were scored 0 with no evidence quoted, so the model did not find the appraisal the coders saw. Human critical 1/2 are concentrated in long calls (mean 18.3 and 36.5 AI sentences vs 7.6 for critical 0).
- Critical 2 (6 calls): the model gave 2 to only 1 of them; 4 were scored 1 (TR100, TR110, TR116, TR244) and 1 was scored 0 (TR124). It also gave 2 to TR163, which the human codes score 0.

**Applied (38 disagreements; model lower on 28).** The main miss flipped direction after the sheet-aligned prompt: 26 human applied 2 calls are now scored 1, against 6 human 1 scored 2. In the calls read for exemplar selection (e.g. TR024, TR094, TR109), the human codes give applied 2 to AI described across many functions or products without a measured result, which the prompt's "a plan to use AI in several units is not 2 by itself" pushes to 1.

**Conceptual (27 disagreements).** Mostly human 2 scored 1 (15 calls); 7 human 1 scored 2. Conceptual 0 is rare in the human codes (3 calls) and the model gave 1 to all 3.
