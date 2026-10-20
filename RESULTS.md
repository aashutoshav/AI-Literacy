# AI Literacy Coding — Results

Gemma 4 12B-it scores the AI-related text from CEO/executive earnings calls 0–2 on four AI-literacy dimensions: **conceptual, critical, applied, governance**. It runs zero-shot with prompt v3, which follows the human coding sheet, and each call is scored 5 times with a per-dimension majority vote (job 6392418). Its scores are compared with the human codes in `data/coding.csv` (143 calls).

## Model vs human codes (n=143)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .568 | .586 | .603 | 82.5% (118/143) |
| Critical | .542 | .550 | .569 | 80.4% (115/143) |
| Applied | .365 | .480 | .373 | 55.9% (80/143) |
| Governance | .633 | .708 | .658 | 82.5% (118/143) |
| Overall four-dimension average | .516 | .743 | .683 | 29.4% (42/143) |

Overall average: ICC(A,1) = **.744** (95% bootstrap CI .643–.816). Mean absolute difference between model and human codes = 0.206 points on the 0–2 scale.

## Human benchmark

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .817 | .824 | .848 | 90.5% (38/42) |
| Critical | .700 | .674 | .711 | 83.3% (35/42) |
| Applied | .824 | .806 | .830 | 90.5% (38/42) |
| Governance | .705 | .784 | .751 | 81.0% (34/42) |
| Overall four-dimension average | .738 | .846 | .858 | 61.9% (26/42) |

Overall average: ICC(A,1) = **.849** (95% bootstrap CI .695–.942). Mean absolute difference between coders = 0.143 points on the 0–2 scale.

Note: this is human vs human on 42 cases; the model is scored against the human codes on 143 cases, so the comparison is indicative, not like-for-like.

## Side by side

| Dimension | Model linear κ | Human linear κ | Model α | Human α | Model exact | Human exact |
|---|---:|---:|---:|---:|---:|---:|
| Conceptual | .568 | .817 | .603 | .848 | 82.5% | 90.5% |
| Critical | .542 | .700 | .569 | .711 | 80.4% | 83.3% |
| Applied | .365 | .824 | .373 | .830 | 55.9% | 90.5% |
| Governance | .633 | .705 | .658 | .751 | 82.5% | 81.0% |
| Overall four-dimension average | .516 | .738 | .683 | .858 | 29.4% | 61.9% |

## Metrics key

- **Linear weighted κ:** chance-corrected agreement; off by 1 counts half as bad as off by 2. Primary measure.
- **Quadratic weighted κ:** same, but the penalty grows with the square of the distance.
- **Ordinal Krippendorff's α:** chance-corrected reliability for ordered scores.
- **Exact agreement:** share of cases with identical scores (k/n). On the overall row, all four dimensions must match.
- **Overall four-dimension average:** each case's mean of its four scores.
- **ICC(A,1):** absolute agreement on the overall average, single rater.

Other runs, run details, method notes and how to reproduce: [EXHAUSTIVE.md](EXHAUSTIVE.md).
