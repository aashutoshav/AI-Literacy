from __future__ import annotations
"""CLI: code AI-literacy dimensions with Gemma 4 IT (transformers + accelerate)."""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from .prompts import build_messages
from .schema import (
    SCORE_DIMS,
    blank_result,
    coerce_result,
    normalize_gold_frame,
    validate_result,
)

TEXT_COL_CANDIDATES = ("AI-related sentences", "ai_related_sentences", "text")


def _load_config(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    with path.open() as f:
        return yaml.safe_load(f) or {}


def _resolve_text_col(columns: list[str]) -> str:
    for c in TEXT_COL_CANDIDATES:
        if c in columns:
            return c
    raise KeyError(f"No text column found; tried {TEXT_COL_CANDIDATES}")


def _extract_json(text: str) -> dict[str, Any]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if not m:
            raise
        return json.loads(m.group(0))


def _mock_code_row(uid: str, sentences: str) -> dict[str, Any]:
    """Deterministic dry-run coder when the model is unavailable."""
    out = blank_result(uid)
    s = (sentences or "").lower()
    rules = {
        "conceptual": ["machine learning", "model", "neural", "algorithm", "pattern"],
        "critical": ["risk", "bias", "hallucin", "limit", "uncertain", "ethic"],
        "applied": ["deploy", "product", "customer", "automat", "forecast", "chatbot"],
        "governance": ["govern", "policy", "committee", "compliance", "oversight", "board"],
    }
    for dim, kws in rules.items():
        hits = [kw for kw in kws if kw in s]
        if len(hits) >= 2:
            out["scores"][dim] = 2
        elif hits:
            out["scores"][dim] = 1
        if out["scores"][dim] >= 1:
            # quote first line/bullet containing a hit
            for line in re.split(r"[\n•]+", sentences or ""):
                low = line.lower()
                if any(h in low for h in hits):
                    out["evidence"][dim] = [line.strip()[:240]]
                    break
    out["notes"] = "dry-run mock coder"
    return out


def _set_hf_cache(cache_path: str | None) -> None:
    if not cache_path:
        return
    p = Path(cache_path).expanduser()
    try:
        p.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print(f"[warn] could not create HF cache at {p}: {e}")
    os.environ.setdefault("HF_HOME", str(p))
    os.environ.setdefault("TRANSFORMERS_CACHE", str(p))
    os.environ.setdefault("HF_HUB_CACHE", str(p / "hub"))


def _load_model(model_id: str, device_map: str = "auto", dtype: str = "auto"):
    """Load Gemma 4 IT for text coding. Prefer CausalLM (text-only); multimodal needs pillow and is unused here."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch_dtype = dtype
    if dtype == "auto":
        torch_dtype = torch.bfloat16 if torch.cuda.is_available() else torch.float32
    elif isinstance(dtype, str) and hasattr(torch, dtype):
        torch_dtype = getattr(torch, dtype)

    if not torch.cuda.is_available():
        print("[warn] CUDA not available — inference will be on CPU", flush=True)
    else:
        print(f"[info] CUDA device: {torch.cuda.get_device_name(0)}  mem_gb={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}", flush=True)

    # Text-only path (earnings-call coding does not need vision/audio)
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map=device_map,
        dtype=torch_dtype,
        attn_implementation="sdpa",
    )
    model.eval()
    # Surface accidental CPU offload early
    try:
        hf_device_map = getattr(model, "hf_device_map", None)
        if hf_device_map:
            offline = sorted({str(v) for v in hf_device_map.values()})
            print(f"[info] hf_device_map devices: {offline}", flush=True)
            if any(str(v) in {"cpu", "disk"} for v in hf_device_map.values()):
                print("[warn] model partially offloaded to cpu/disk — expect slow inference; request a larger GPU", flush=True)
    except Exception:
        pass
    return {"kind": "causal", "model": model, "tokenizer": tokenizer}


def _generate(bundle: dict, messages: list[dict[str, str]], max_new_tokens: int, temperature: float) -> str:
    model = bundle["model"]
    tokenizer = bundle["tokenizer"]

    if hasattr(tokenizer, "apply_chat_template"):
        prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    else:
        prompt = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in messages) + "\nASSISTANT:"

    inputs = tokenizer(prompt, return_tensors="pt")
    if hasattr(model, "device"):
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
    else:
        try:
            inputs = {k: v.to(next(model.parameters()).device) for k, v in inputs.items()}
        except StopIteration:
            pass

    gen_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": temperature is not None and temperature > 0,
    }
    if gen_kwargs["do_sample"]:
        gen_kwargs["temperature"] = temperature

    output_ids = model.generate(**inputs, **gen_kwargs)
    new_tokens = output_ids[0][inputs["input_ids"].shape[-1] :]
    return tokenizer.decode(new_tokens, skip_special_tokens=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gemma 4 AI-literacy coding CLI")
    parser.add_argument("--config", type=Path, default=Path("configs/default.yaml"))
    parser.add_argument("--csv", type=Path, default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--model-id", type=str, default=None)
    parser.add_argument("--output-jsonl", type=Path, default=None)
    parser.add_argument("--output-csv", type=Path, default=None)
    parser.add_argument("--dry-run", action="store_true", help="Mock coder; no model download")
    parser.add_argument("--hf-cache", type=str, default=None)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--shots", type=int, default=0, help="Number of few-shot exemplars (0 = zero-shot)")
    parser.add_argument(
        "--exemplars",
        type=Path,
        default=Path("configs/fewshot_exemplars.json"),
        help="JSON file with {exemplars: [...]} gold examples",
    )
    parser.add_argument(
        "--exclude-exemplars",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="When shots>0, skip exemplar uids in the eval set (default: true)",
    )
    args = parser.parse_args(argv)

    cfg = _load_config(args.config)
    paths = cfg.get("paths") or {}
    model_cfg = cfg.get("model") or {}
    inf_cfg = cfg.get("inference") or {}

    cache = args.hf_cache or paths.get("hf_cache") or os.environ.get("HF_HOME")
    _set_hf_cache(cache)

    seed = args.seed if args.seed is not None else int(cfg.get("seed", 42))
    csv_path = args.csv or Path(paths.get("data_csv", "coding.csv"))
    limit = args.limit if args.limit is not None else inf_cfg.get("limit")
    dry_run = bool(args.dry_run or inf_cfg.get("dry_run", False))
    model_id = args.model_id or model_cfg.get("model_id", "google/gemma-4-12B-it")
    out_jsonl = args.output_jsonl or Path(paths.get("preds_jsonl", "outputs/preds.jsonl"))
    out_csv = args.output_csv or Path(paths.get("preds_csv", "outputs/preds.csv"))

    try:
        import random
        import numpy as np
        random.seed(seed)
        np.random.seed(seed)
    except ImportError:
        pass

    import pandas as pd

    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        return 1

    df = pd.read_csv(csv_path)
    df = normalize_gold_frame(df)
    text_col = _resolve_text_col(list(df.columns))

    exemplars: list[dict[str, Any]] = []
    shots = int(args.shots or 0)
    if shots > 0:
        ex_path = args.exemplars
        if not ex_path.exists():
            print(f"ERROR: exemplars file not found: {ex_path}", file=sys.stderr)
            return 1
        ex_blob = json.loads(ex_path.read_text())
        exemplars = list(ex_blob.get("exemplars") or [])[:shots]
        print(f"[info] few-shot shots={len(exemplars)} from {ex_path}", flush=True)
        if args.exclude_exemplars:
            ex_uids = {str(e.get("uid", "")) for e in exemplars}
            before = len(df)
            uid_col = "uid" if "uid" in df.columns else None
            if uid_col:
                df = df[~df[uid_col].astype(str).isin(ex_uids)].copy()
                print(f"[info] excluded exemplar uids from eval: {before} -> {len(df)}", flush=True)

    if limit is not None:
        df = df.head(int(limit))

    bundle = None
    if not dry_run:
        try:
            bundle = _load_model(
                model_id,
                device_map=model_cfg.get("device_map", "auto"),
                dtype=str(model_cfg.get("dtype", "auto")),
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] model load failed ({exc}); falling back to --dry-run mock", file=sys.stderr)
            dry_run = True

    results: list[dict[str, Any]] = []
    max_new = int(model_cfg.get("max_new_tokens", 1024))
    temperature = float(model_cfg.get("temperature", 0.0))

    for _, row in df.iterrows():
        uid = str(row.get("uid", ""))
        sentences = str(row.get(text_col, "") or "")
        if dry_run or bundle is None:
            result = _mock_code_row(uid, sentences)
        else:
            messages = build_messages(
                uid=uid,
                executive=str(row.get("executive", "") or ""),
                company=str(row.get("company", "") or ""),
                call_date=str(row.get("call_date", "") or ""),
                sentences=sentences,
                exemplars=exemplars or None,
            )
            raw = _generate(bundle, messages, max_new_tokens=max_new, temperature=temperature)
            try:
                parsed = _extract_json(raw)
                result = coerce_result(parsed, uid=uid)
            except Exception as exc:  # noqa: BLE001
                result = blank_result(uid)
                result["notes"] = f"parse_error: {exc}; raw={raw[:500]}"

        errs = validate_result(result, require_evidence_for_nonzero=False)
        result["validation_warnings"] = errs
        results.append(result)
        print(f"coded uid={uid} scores={result['scores']}")

    out_jsonl.parent.mkdir(parents=True, exist_ok=True)
    out_csv.parent.mkdir(parents=True, exist_ok=True)

    with out_jsonl.open("w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    flat = []
    for r in results:
        row = {"uid": r["uid"], "notes": r.get("notes", "")}
        for d in SCORE_DIMS:
            row[f"pred_{d}"] = r["scores"][d]
            row[f"evidence_{d}"] = " | ".join(r["evidence"].get(d) or [])
        flat.append(row)
    pd.DataFrame(flat).to_csv(out_csv, index=False)

    print(f"wrote {out_jsonl} and {out_csv} (n={len(results)}, dry_run={dry_run})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
