# Plan of action — AI literacy Gemma coding

1. **Env on ICE** — create `ai_literacy` under `conda_envs` (same pattern as `c21u`), set `HF_HOME` to `scratch/hf_cache`, install torch (CUDA) + transformers for Gemma 4.
2. **Project layout** — sync this repo + `coding.csv` to `scratch/ai_literacy`; use `scripts/run_code_gemma.sbatch` (mirrors your `ice-gpu` / `coc` / `coc-ice` sample).
3. **Grounded coding** — rubric for conceptual / critical / applied / governance (0–2), JSON + evidence quotes, few-shots from labeled CSV, agreement metrics vs humans.
4. **Validation run** — small GPU job (`LIMIT=10` then full 85), compare to gold with `python -m src.validate`.
5. **Later** — CEO gender join + market-response analysis (does not block env setup).
