# n=200 comparison (data/coding_n200.csv)

Sorted by mean per-dimension linear weighted κ. Overall = four-dimension average (composite); joint exact = all four dimensions match.

| Run | Prompt | Model | Mode | Con lin κ | Cri lin κ | App lin κ | Gov lin κ | Mean lin κ | Overall lin κ | Overall quad κ | Overall ord α | ICC(A,1) [95% CI] | MAD | Joint exact | n |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|---:|
| v3_fs10_31b | v3 | 31B | few-shot (10 boundary) | .271 | .329 | .531 | .547 | .419 | .439 | .653 | .647 | .654 [.573–.722] | 0.255 | 23.5% | 200 |
| v4_fs10_12b | v4 | 12B | few-shot (10 boundary) | .307 | .381 | .547 | .442 | .419 | .452 | .661 | .675 | .662 [.580–.730] | 0.251 | 24.0% | 200 |
| v4_fs10_31b | v4 | 31B | few-shot (10 boundary) | .283 | .342 | .507 | .534 | .417 | .411 | .626 | .630 | .628 [.549–.695] | 0.263 | 25.0% | 200 |
| v3_fs10_12b | v3 | 12B | few-shot (10 boundary) | .283 | .373 | .541 | .468 | .416 | .449 | .653 | .659 | .654 [.567–.727] | 0.256 | 22.5% | 200 |
| v3_zs_12b | v3 | 12B | zero-shot | .208 | .354 | .544 | .542 | .412 | .452 | .650 | .661 | .651 [.565–.722] | 0.244 | 25.0% | 200 |
| v3_vote5_12b | v3 | 12B | vote5 | .226 | .354 | .532 | .529 | .411 | .460 | .666 | .676 | .667 [.585–.734] | 0.237 | 24.5% | 200 |
| ens_v4_12b31b_v3_12b | ensemble | mixed | majority: v4 12B zero + v4 31B zero + v3 12B zero | .217 | .354 | .484 | .542 | .399 | .417 | .605 | .625 | .606 [.514–.685] | 0.253 | 27.5% | 200 |
| ens_best3_old | ensemble | mixed | majority of the best 3 on old n=143 data (v4 12B zero, v3 12B vote5, sheet-aligned 31B zero) | .217 | .354 | .484 | .542 | .399 | .417 | .605 | .625 | .606 [.514–.685] | 0.253 | 27.5% | 200 |
| ens_xprompt_12b | ensemble | mixed | majority across prompts at 12B (v4/v3/sheet-aligned zero) | .217 | .354 | .477 | .542 | .398 | .420 | .600 | .621 | .601 [.507–.684] | 0.249 | 28.0% | 200 |
| v4_zs_12b | v4 | 12B | zero-shot | .214 | .354 | .469 | .518 | .389 | .417 | .598 | .614 | .599 [.505–.680] | 0.253 | 27.5% | 200 |
| v4_perdim_12b | v4 | 12B | per-dimension | .302 | .337 | .421 | .467 | .382 | .446 | .640 | .657 | .641 [.559–.711] | 0.245 | 27.5% | 200 |
| ens_v4_trio | ensemble | mixed | majority: v4 12B zero + v4 31B zero + v4 12B vote5 | .211 | .332 | .475 | .505 | .381 | .419 | .589 | .608 | .591 [.495–.673] | 0.253 | 28.0% | 200 |
| v4_vote5_12b | v4 | 12B | vote5 | .224 | .332 | .469 | .493 | .380 | .417 | .589 | .607 | .590 [.494–.672] | 0.253 | 28.0% | 200 |
| ens_zs6_mean | ensemble | mixed | mean of all six zero-shot runs, rounded; exact .5 toward v4 12B | .192 | .356 | .489 | .478 | .379 | .400 | .577 | .610 | .578 [.487–.661] | 0.256 | 27.5% | 200 |
| ens_zs6 | ensemble | mixed | majority of all six zero-shot runs (3 prompts x 2 models); tie -> v4 12B if tied, else lower | .192 | .356 | .489 | .478 | .379 | .400 | .577 | .610 | .578 [.487–.661] | 0.256 | 27.5% | 200 |
| v3_zs_31b | v3 | 31B | zero-shot | .208 | .329 | .543 | .401 | .370 | .426 | .624 | .659 | .625 [.542–.698] | 0.249 | 23.0% | 200 |
| sheet_fs10_12b | sheet-aligned | 12B | few-shot (10 boundary) | .290 | .355 | .562 | .271 | .369 | .396 | .603 | .609 | .605 [.514–.683] | 0.274 | 23.0% | 200 |
| v3_vote5_31b | v3 | 31B | vote5 | .211 | .329 | .528 | .401 | .367 | .420 | .621 | .653 | .622 [.538–.695] | 0.251 | 22.0% | 200 |
| ens_v4_12b31b_sheet12b | ensemble | mixed | majority: v4 12B zero + v4 31B zero + sheet-aligned 12B zero | .189 | .356 | .440 | .478 | .366 | .391 | .563 | .596 | .564 [.471–.647] | 0.259 | 27.5% | 200 |
| v4_zs_31b | v4 | 31B | zero-shot | .186 | .329 | .458 | .486 | .365 | .359 | .542 | .589 | .544 [.457–.624] | 0.271 | 26.5% | 200 |
| v4_vote5_31b | v4 | 31B | vote5 | .183 | .319 | .468 | .476 | .361 | .369 | .552 | .595 | .553 [.463–.632] | 0.269 | 27.0% | 200 |
| ens_xprompt_31b | ensemble | mixed | majority across prompts at 31B (v4/v3/sheet-aligned zero); tie -> v4 31B | .186 | .329 | .474 | .401 | .347 | .357 | .533 | .574 | .535 [.444–.619] | 0.273 | 26.5% | 200 |
| sheet_fs10_31b | sheet-aligned | 31B | few-shot (10 boundary) | .249 | .327 | .551 | .210 | .334 | .383 | .573 | .599 | .574 [.490–.648] | 0.270 | 25.5% | 200 |
| sheet_vote5_12b | sheet-aligned | 12B | vote5 | .195 | .318 | .423 | .226 | .290 | .341 | .489 | .498 | .490 [.379–.586] | 0.278 | 27.5% | 200 |
| sheet_zs_12b | sheet-aligned | 12B | zero-shot | .182 | .327 | .423 | .226 | .289 | .343 | .493 | .508 | .494 [.384–.591] | 0.275 | 27.5% | 200 |
| sheet_vote5_31b | sheet-aligned | 31B | vote5 | .193 | .357 | .466 | .142 | .289 | .317 | .491 | .528 | .492 [.401–.575] | 0.289 | 25.5% | 200 |
| sheet_zs_31b | sheet-aligned | 31B | zero-shot | .186 | .357 | .466 | .142 | .288 | .319 | .492 | .534 | .494 [.403–.578] | 0.287 | 25.5% | 200 |

Human inter-coder reference (advisor table, Lee vs Elsie, n=42 older calls; lin κ / quad κ / ord α / exact):

- conceptual: .817 / .824 / .848 / 90.5% (38/42)
- critical: .700 / .674 / .711 / 83.3% (35/42)
- applied: .824 / .806 / .830 / 90.5% (38/42)
- governance: .705 / .784 / .751 / 81.0% (34/42)
- overall: .738 / .846 / .858 / 61.9% (26/42)

## Score distributions (% of calls at 0 / 1 / 2)

| Run | Conceptual | Critical | Applied | Governance |
|---|---|---|---|---|
| human codes | 10 / 50 / 39 | 74 / 24 / 2 | 15 / 48 / 36 | 86 / 12 / 2 |
| v4_zs_12b | 14 / 76 / 10 | 86 / 12 / 2 | 22 / 60 / 18 | 84 / 15 / 0 |
| v4_zs_31b | 14 / 76 / 10 | 89 / 10 / 0 | 24 / 62 / 15 | 89 / 11 / 0 |
| v3_zs_12b | 14 / 76 / 10 | 86 / 12 / 2 | 24 / 36 / 40 | 86 / 14 / 0 |
| v3_zs_31b | 14 / 76 / 10 | 89 / 10 / 0 | 26 / 32 / 42 | 91 / 8 / 0 |
| sheet_zs_12b | 13 / 78 / 9 | 84 / 15 / 0 | 17 / 68 / 16 | 93 / 6 / 0 |
| sheet_zs_31b | 14 / 76 / 10 | 88 / 12 / 0 | 24 / 61 / 16 | 96 / 4 / 0 |
| v4_vote5_12b | 14 / 76 / 10 | 86 / 12 / 1 | 22 / 60 / 18 | 85 / 14 / 0 |
| v4_vote5_31b | 14 / 76 / 10 | 88 / 11 / 0 | 24 / 61 / 15 | 89 / 10 / 0 |
| v3_vote5_12b | 12 / 77 / 11 | 86 / 12 / 2 | 24 / 36 / 41 | 85 / 14 / 0 |
| v3_vote5_31b | 13 / 76 / 10 | 89 / 10 / 0 | 26 / 31 / 42 | 91 / 8 / 0 |
| sheet_vote5_12b | 14 / 78 / 9 | 84 / 16 / 0 | 17 / 68 / 16 | 93 / 6 / 0 |
| sheet_vote5_31b | 14 / 77 / 9 | 88 / 12 / 0 | 24 / 61 / 16 | 96 / 4 / 0 |
| v4_fs10_12b | 17 / 64 / 19 | 78 / 19 / 2 | 29 / 42 / 28 | 88 / 11 / 1 |
| v4_fs10_31b | 16 / 68 / 16 | 88 / 10 / 1 | 30 / 46 / 24 | 89 / 10 / 2 |
| v3_fs10_12b | 18 / 64 / 18 | 78 / 20 / 2 | 31 / 34 / 36 | 88 / 12 / 1 |
| v3_fs10_31b | 16 / 68 / 15 | 89 / 10 / 0 | 34 / 33 / 33 | 90 / 9 / 2 |
| sheet_fs10_12b | 18 / 64 / 18 | 81 / 17 / 2 | 30 / 42 / 29 | 93 / 6 / 0 |
| sheet_fs10_31b | 16 / 68 / 16 | 86 / 12 / 2 | 28 / 46 / 26 | 94 / 5 / 0 |
| v4_perdim_12b | 14 / 70 / 16 | 82 / 15 / 3 | 28 / 60 / 12 | 79 / 20 / 0 |
| ens_v4_12b31b_sheet12b | 14 / 77 / 10 | 86 / 14 / 0 | 21 / 63 / 16 | 88 / 12 / 0 |
| ens_v4_12b31b_v3_12b | 13 / 77 / 10 | 86 / 12 / 2 | 23 / 58 / 19 | 86 / 14 / 0 |
| ens_v4_trio | 14 / 76 / 10 | 86 / 12 / 1 | 23 / 60 / 18 | 86 / 14 / 0 |
| ens_xprompt_12b | 13 / 77 / 10 | 86 / 12 / 2 | 20 / 62 / 18 | 86 / 14 / 0 |
| ens_xprompt_31b | 14 / 76 / 10 | 89 / 10 / 0 | 24 / 60 / 16 | 91 / 8 / 0 |
| ens_zs6 | 13 / 78 / 10 | 86 / 14 / 0 | 22 / 58 / 19 | 88 / 12 / 0 |
| ens_zs6_mean | 13 / 78 / 10 | 86 / 14 / 0 | 22 / 58 / 19 | 88 / 12 / 0 |
| ens_best3_old | 13 / 77 / 10 | 86 / 12 / 2 | 23 / 58 / 19 | 86 / 14 / 0 |

## Ensembles

- ens_v4_12b31b_sheet12b: majority: v4 12B zero + v4 31B zero + sheet-aligned 12B zero (first member breaks ties)
- ens_v4_12b31b_v3_12b: majority: v4 12B zero + v4 31B zero + v3 12B zero (first member breaks ties)
- ens_v4_trio: majority: v4 12B zero + v4 31B zero + v4 12B vote5 (first member breaks ties)
- ens_xprompt_12b: majority across prompts at 12B (v4/v3/sheet-aligned zero) (first member breaks ties)
- ens_xprompt_31b: majority across prompts at 31B (v4/v3/sheet-aligned zero); tie -> v4 31B (first member breaks ties)
- ens_zs6: majority of all six zero-shot runs (3 prompts x 2 models); tie -> v4 12B if tied, else lower (first member breaks ties)
- ens_zs6_mean: mean of all six zero-shot runs, rounded; exact .5 toward v4 12B (first member breaks ties)
- ens_best3_old: majority of the best 3 on old n=143 data (v4 12B zero, v3 12B vote5, sheet-aligned 31B zero) (first member breaks ties)

## Per-run tables

### v4_zs_12b — v4, 12B, zero-shot

`outputs/preds_fix4_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .214 | .347 | .291 | 51.0% (102/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .469 | .580 | .560 | 62.5% (125/200) |
| Governance | .518 | .550 | .573 | 87.0% (174/200) |
| Overall four-dimension average | .417 | .598 | .614 | 27.5% (55/200) |

ICC(A,1) = .599 (95% bootstrap CI .505–.680); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.557.

### v4_zs_31b — v4, 31B, zero-shot

`outputs/preds_fix4_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .186 | .325 | .267 | 49.0% (98/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .458 | .584 | .553 | 61.0% (122/200) |
| Governance | .486 | .516 | .532 | 88.0% (176/200) |
| Overall four-dimension average | .359 | .542 | .589 | 26.5% (53/200) |

ICC(A,1) = .544 (95% bootstrap CI .457–.624); mean |human − model| = 0.271; composite mean human 0.738 vs model 0.524.

### v3_zs_12b — v3, 12B, zero-shot

`outputs/preds_fix3_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .208 | .329 | .273 | 51.0% (102/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .544 | .649 | .655 | 65.0% (130/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .452 | .650 | .661 | 25.0% (50/200) |

ICC(A,1) = .651 (95% bootstrap CI .565–.722); mean |human − model| = 0.244; composite mean human 0.738 vs model 0.606.

### v3_zs_31b — v3, 31B, zero-shot

`outputs/preds_fix3_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .208 | .342 | .291 | 50.5% (101/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .543 | .662 | .646 | 63.5% (127/200) |
| Governance | .401 | .462 | .454 | 86.5% (173/200) |
| Overall four-dimension average | .426 | .624 | .659 | 23.0% (46/200) |

ICC(A,1) = .625 (95% bootstrap CI .542–.698); mean |human − model| = 0.249; composite mean human 0.738 vs model 0.584.

### sheet_zs_12b — sheet-aligned, 12B, zero-shot

`outputs/preds_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .182 | .316 | .255 | 49.5% (99/200) |
| Critical | .327 | .360 | .353 | 76.5% (153/200) |
| Applied | .423 | .539 | .517 | 61.0% (122/200) |
| Governance | .226 | .284 | .253 | 84.0% (168/200) |
| Overall four-dimension average | .343 | .493 | .508 | 27.5% (55/200) |

ICC(A,1) = .494 (95% bootstrap CI .384–.591); mean |human − model| = 0.275; composite mean human 0.738 vs model 0.545.

### sheet_zs_31b — sheet-aligned, 31B, zero-shot

`outputs/preds_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .186 | .325 | .267 | 49.0% (98/200) |
| Critical | .357 | .389 | .379 | 78.5% (157/200) |
| Applied | .466 | .590 | .561 | 61.5% (123/200) |
| Governance | .142 | .184 | .143 | 84.5% (169/200) |
| Overall four-dimension average | .319 | .492 | .534 | 25.5% (51/200) |

ICC(A,1) = .494 (95% bootstrap CI .403–.578); mean |human − model| = 0.287; composite mean human 0.738 vs model 0.512.

### v4_vote5_12b — v4, 12B, vote5

`outputs/preds_fix4_vote5_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .224 | .360 | .302 | 51.0% (102/200) |
| Critical | .332 | .377 | .363 | 77.0% (154/200) |
| Applied | .469 | .580 | .560 | 62.5% (125/200) |
| Governance | .493 | .530 | .548 | 86.5% (173/200) |
| Overall four-dimension average | .417 | .589 | .607 | 28.0% (56/200) |

ICC(A,1) = .590 (95% bootstrap CI .494–.672); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.552.

### v4_vote5_31b — v4, 31B, vote5

`outputs/preds_fix4_vote5_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .183 | .325 | .267 | 48.5% (97/200) |
| Critical | .319 | .357 | .335 | 77.5% (155/200) |
| Applied | .468 | .592 | .561 | 61.5% (123/200) |
| Governance | .476 | .521 | .534 | 87.5% (175/200) |
| Overall four-dimension average | .369 | .552 | .595 | 27.0% (54/200) |

ICC(A,1) = .553 (95% bootstrap CI .463–.632); mean |human − model| = 0.269; composite mean human 0.738 vs model 0.524.

### v3_vote5_12b — v3, 12B, vote5

`outputs/preds_fix3_vote5_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .226 | .350 | .299 | 52.5% (105/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .532 | .650 | .651 | 63.5% (127/200) |
| Governance | .529 | .561 | .587 | 87.5% (175/200) |
| Overall four-dimension average | .460 | .666 | .676 | 24.5% (49/200) |

ICC(A,1) = .667 (95% bootstrap CI .585–.734); mean |human − model| = 0.237; composite mean human 0.738 vs model 0.618.

### v3_vote5_31b — v3, 31B, vote5

`outputs/preds_fix3_vote5_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .211 | .342 | .291 | 51.0% (102/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .528 | .652 | .635 | 62.0% (124/200) |
| Governance | .401 | .462 | .454 | 86.5% (173/200) |
| Overall four-dimension average | .420 | .621 | .653 | 22.0% (44/200) |

ICC(A,1) = .622 (95% bootstrap CI .538–.695); mean |human − model| = 0.251; composite mean human 0.738 vs model 0.586.

### sheet_vote5_12b — sheet-aligned, 12B, vote5

`outputs/preds_vote5_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .195 | .329 | .267 | 50.0% (100/200) |
| Critical | .318 | .351 | .344 | 76.0% (152/200) |
| Applied | .423 | .527 | .505 | 61.5% (123/200) |
| Governance | .226 | .284 | .253 | 84.0% (168/200) |
| Overall four-dimension average | .341 | .489 | .498 | 27.5% (55/200) |

ICC(A,1) = .490 (95% bootstrap CI .379–.586); mean |human − model| = 0.278; composite mean human 0.738 vs model 0.545.

### sheet_vote5_31b — sheet-aligned, 31B, vote5

`outputs/preds_vote5_zeroshot_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .193 | .330 | .271 | 49.5% (99/200) |
| Critical | .357 | .389 | .379 | 78.5% (157/200) |
| Applied | .466 | .590 | .561 | 61.5% (123/200) |
| Governance | .142 | .184 | .143 | 84.5% (169/200) |
| Overall four-dimension average | .317 | .491 | .528 | 25.5% (51/200) |

ICC(A,1) = .492 (95% bootstrap CI .401–.575); mean |human − model| = 0.289; composite mean human 0.738 vs model 0.511.

### v4_fs10_12b — v4, 12B, few-shot (10 boundary)

`outputs/preds_fix4_fewshot_boundary10_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .307 | .425 | .407 | 54.5% (109/200) |
| Critical | .381 | .437 | .422 | 75.5% (151/200) |
| Applied | .547 | .634 | .628 | 66.0% (132/200) |
| Governance | .442 | .503 | .468 | 86.0% (172/200) |
| Overall four-dimension average | .452 | .661 | .675 | 24.0% (48/200) |

ICC(A,1) = .662 (95% bootstrap CI .580–.730); mean |human − model| = 0.251; composite mean human 0.738 vs model 0.596.

### v4_fs10_31b — v4, 31B, few-shot (10 boundary)

`outputs/preds_fix4_fewshot_boundary10_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .283 | .397 | .370 | 54.0% (108/200) |
| Critical | .342 | .413 | .376 | 77.5% (155/200) |
| Applied | .507 | .594 | .581 | 63.5% (127/200) |
| Governance | .534 | .592 | .540 | 88.5% (177/200) |
| Overall four-dimension average | .411 | .626 | .630 | 25.0% (50/200) |

ICC(A,1) = .628 (95% bootstrap CI .549–.695); mean |human − model| = 0.263; composite mean human 0.738 vs model 0.547.

### v3_fs10_12b — v3, 12B, few-shot (10 boundary)

`outputs/preds_fix3_fewshot_boundary10_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .283 | .398 | .374 | 53.0% (106/200) |
| Critical | .373 | .429 | .413 | 75.0% (150/200) |
| Applied | .541 | .630 | .631 | 64.5% (129/200) |
| Governance | .468 | .524 | .497 | 86.5% (173/200) |
| Overall four-dimension average | .449 | .653 | .659 | 22.5% (45/200) |

ICC(A,1) = .654 (95% bootstrap CI .567–.727); mean |human − model| = 0.256; composite mean human 0.738 vs model 0.606.

### v3_fs10_31b — v3, 31B, few-shot (10 boundary)

`outputs/preds_fix3_fewshot_boundary10_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .271 | .377 | .347 | 53.5% (107/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .531 | .617 | .619 | 63.5% (127/200) |
| Governance | .547 | .604 | .554 | 89.0% (178/200) |
| Overall four-dimension average | .439 | .653 | .647 | 23.5% (47/200) |

ICC(A,1) = .654 (95% bootstrap CI .573–.722); mean |human − model| = 0.255; composite mean human 0.738 vs model 0.552.

### sheet_fs10_12b — sheet-aligned, 12B, few-shot (10 boundary)

`outputs/preds_fewshot_boundary10_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .290 | .402 | .378 | 53.5% (107/200) |
| Critical | .355 | .409 | .385 | 75.5% (151/200) |
| Applied | .562 | .637 | .634 | 67.5% (135/200) |
| Governance | .271 | .359 | .310 | 84.5% (169/200) |
| Overall four-dimension average | .396 | .603 | .609 | 23.0% (46/200) |

ICC(A,1) = .605 (95% bootstrap CI .514–.683); mean |human − model| = 0.274; composite mean human 0.738 vs model 0.569.

### sheet_fs10_31b — sheet-aligned, 31B, few-shot (10 boundary)

`outputs/preds_fewshot_boundary10_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .249 | .368 | .342 | 52.0% (104/200) |
| Critical | .327 | .383 | .366 | 76.5% (153/200) |
| Applied | .551 | .632 | .623 | 67.0% (134/200) |
| Governance | .210 | .275 | .232 | 84.5% (169/200) |
| Overall four-dimension average | .383 | .573 | .599 | 25.5% (51/200) |

ICC(A,1) = .574 (95% bootstrap CI .490–.648); mean |human − model| = 0.270; composite mean human 0.738 vs model 0.547.

### v4_perdim_12b — v4, 12B, per-dimension

`outputs/preds_fix4_perdim_zeroshot_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .302 | .428 | .400 | 55.5% (111/200) |
| Critical | .337 | .413 | .381 | 74.5% (149/200) |
| Applied | .421 | .521 | .480 | 59.0% (118/200) |
| Governance | .467 | .527 | .515 | 83.0% (166/200) |
| Overall four-dimension average | .446 | .640 | .657 | 27.5% (55/200) |

ICC(A,1) = .641 (95% bootstrap CI .559–.711); mean |human − model| = 0.245; composite mean human 0.738 vs model 0.573.

### ens_v4_12b31b_sheet12b — ensemble, mixed, majority: v4 12B zero + v4 31B zero + sheet-aligned 12B zero

`outputs/preds_ens_v4_12b31b_sheet12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .189 | .325 | .267 | 49.5% (99/200) |
| Critical | .356 | .386 | .381 | 78.0% (156/200) |
| Applied | .440 | .564 | .541 | 60.5% (121/200) |
| Governance | .478 | .520 | .535 | 87.0% (174/200) |
| Overall four-dimension average | .391 | .563 | .596 | 27.5% (55/200) |

ICC(A,1) = .564 (95% bootstrap CI .471–.647); mean |human − model| = 0.259; composite mean human 0.738 vs model 0.546.

### ens_v4_12b31b_v3_12b — ensemble, mixed, majority: v4 12B zero + v4 31B zero + v3 12B zero

`outputs/preds_ens_v4_12b31b_v3_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .217 | .346 | .291 | 51.5% (103/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .484 | .596 | .577 | 63.0% (126/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .417 | .605 | .625 | 27.5% (55/200) |

ICC(A,1) = .606 (95% bootstrap CI .514–.685); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.557.

### ens_v4_trio — ensemble, mixed, majority: v4 12B zero + v4 31B zero + v4 12B vote5

`outputs/preds_ens_v4_trio_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .211 | .347 | .291 | 50.5% (101/200) |
| Critical | .332 | .377 | .363 | 77.0% (154/200) |
| Applied | .475 | .587 | .566 | 62.5% (125/200) |
| Governance | .505 | .540 | .561 | 87.0% (174/200) |
| Overall four-dimension average | .419 | .589 | .608 | 28.0% (56/200) |

ICC(A,1) = .591 (95% bootstrap CI .495–.673); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.550.

### ens_xprompt_12b — ensemble, mixed, majority across prompts at 12B (v4/v3/sheet-aligned zero)

`outputs/preds_ens_xprompt_12b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .217 | .346 | .291 | 51.5% (103/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .477 | .583 | .565 | 63.5% (127/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .420 | .600 | .621 | 28.0% (56/200) |

ICC(A,1) = .601 (95% bootstrap CI .507–.684); mean |human − model| = 0.249; composite mean human 0.738 vs model 0.561.

### ens_xprompt_31b — ensemble, mixed, majority across prompts at 31B (v4/v3/sheet-aligned zero); tie -> v4 31B

`outputs/preds_ens_xprompt_31b_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .186 | .325 | .267 | 49.0% (98/200) |
| Critical | .329 | .366 | .345 | 78.0% (156/200) |
| Applied | .474 | .597 | .569 | 62.0% (124/200) |
| Governance | .401 | .462 | .454 | 86.5% (173/200) |
| Overall four-dimension average | .357 | .533 | .574 | 26.5% (53/200) |

ICC(A,1) = .535 (95% bootstrap CI .444–.619); mean |human − model| = 0.273; composite mean human 0.738 vs model 0.522.

### ens_zs6 — ensemble, mixed, majority of all six zero-shot runs (3 prompts x 2 models); tie -> v4 12B if tied, else lower

`outputs/preds_ens_zs6_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .192 | .324 | .267 | 50.0% (100/200) |
| Critical | .356 | .386 | .381 | 78.0% (156/200) |
| Applied | .489 | .608 | .590 | 63.0% (126/200) |
| Governance | .478 | .520 | .535 | 87.0% (174/200) |
| Overall four-dimension average | .400 | .577 | .610 | 27.5% (55/200) |

ICC(A,1) = .578 (95% bootstrap CI .487–.661); mean |human − model| = 0.256; composite mean human 0.738 vs model 0.551.

### ens_zs6_mean — ensemble, mixed, mean of all six zero-shot runs, rounded; exact .5 toward v4 12B

`outputs/preds_ens_zs6_mean_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .192 | .324 | .267 | 50.0% (100/200) |
| Critical | .356 | .386 | .381 | 78.0% (156/200) |
| Applied | .489 | .608 | .590 | 63.0% (126/200) |
| Governance | .478 | .520 | .535 | 87.0% (174/200) |
| Overall four-dimension average | .400 | .577 | .610 | 27.5% (55/200) |

ICC(A,1) = .578 (95% bootstrap CI .487–.661); mean |human − model| = 0.256; composite mean human 0.738 vs model 0.551.

### ens_best3_old — ensemble, mixed, majority of the best 3 on old n=143 data (v4 12B zero, v3 12B vote5, sheet-aligned 31B zero)

`outputs/preds_ens_best3_old_n200.csv`; n=200 (dropped invalid 0, missing 0)

| Dimension | Linear weighted κ | Quadratic weighted κ | Ordinal Krippendorff's α | Exact agreement |
|---|---:|---:|---:|---:|
| Conceptual | .217 | .346 | .291 | 51.5% (103/200) |
| Critical | .354 | .406 | .367 | 77.5% (155/200) |
| Applied | .484 | .596 | .577 | 63.0% (126/200) |
| Governance | .542 | .572 | .601 | 88.0% (176/200) |
| Overall four-dimension average | .417 | .605 | .625 | 27.5% (55/200) |

ICC(A,1) = .606 (95% bootstrap CI .514–.685); mean |human − model| = 0.253; composite mean human 0.738 vs model 0.557.

