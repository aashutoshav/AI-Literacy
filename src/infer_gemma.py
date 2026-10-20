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

from .prompts import build_messages, build_perdim_messages
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


def _generate(
    bundle: dict,
    messages: list[dict[str, str]],
    max_new_tokens: int,
    temperature: float,
    *,
    num_samples: int = 1,
    top_p: float | None = None,
) -> list[str]:
    """Return a list of decoded completions (length num_samples).

    temperature <= 0 -> greedy (one completion, as in the original zero/few-shot runs).
    temperature > 0  -> sampling; num_samples completions drawn in one batched generate call.
    """
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

    do_sample = temperature is not None and temperature > 0
    gen_kwargs = {
        "max_new_tokens": max_new_tokens,
        "do_sample": do_sample,
    }
    if do_sample:
        gen_kwargs["temperature"] = temperature
        if top_p is not None:
            gen_kwargs["top_p"] = top_p
        gen_kwargs["num_return_sequences"] = max(1, int(num_samples))

    output_ids = model.generate(**inputs, **gen_kwargs)
    prompt_len = inputs["input_ids"].shape[-1]
    return [tokenizer.decode(seq[prompt_len:], skip_special_tokens=True) for seq in output_ids]


def _vote(scores: list[int]) -> tuple[int, dict[int, int]]:
    """Majority vote over 0/1/2; ties go to the LOWER score ("between 1 and 2, assign 1")."""
    counts = {k: 0 for k in (0, 1, 2)}
    for v in scores:
        if v in counts:
            counts[v] += 1
    if not scores:
        return 0, counts
    best = max(counts.values())
    winner = min(k for k, c in counts.items() if c == best)
    return winner, counts


def _parse_full(raw: str, uid: str) -> tuple[dict[str, Any] | None, str]:
    try:
        return coerce_result(_extract_json(raw), uid=uid), ""
    except Exception as exc:  # noqa: BLE001
        return None, f"parse_error: {exc}; raw={raw[:300]}"


def _parse_perdim(raw: str, dim: str) -> tuple[tuple[int, list[str], str] | None, str]:
    """Parse {"score": k, "evidence": [...]} (also accepts {"scores": {dim: k}} shapes)."""
    try:
        obj = _extract_json(raw)
    except Exception as exc:  # noqa: BLE001
        return None, f"parse_error: {exc}; raw={raw[:300]}"
    val = obj.get("score")
    if val is None and isinstance(obj.get("scores"), dict):
        val = obj["scores"].get(dim)
    try:
        val = int(val)
    except (TypeError, ValueError):
        return None, f"parse_error: no integer score; raw={raw[:300]}"
    val = max(0, min(2, val))
    ev = obj.get("evidence", [])
    if isinstance(ev, dict):
        ev = ev.get(dim, [])
    if isinstance(ev, str):
        ev = [ev] if ev.strip() else []
    ev = [str(e) for e in (ev or []) if str(e).strip()]
    return (val, ev, str(obj.get("notes", "") or "")), ""


def _code_row(
    bundle: dict,
    *,
    uid: str,
    meta: dict[str, str],
    sentences: str,
    exemplars: list[dict[str, Any]] | None,
    perdim: bool,
    num_samples: int,
    temperature: float,
    top_p: float | None,
    max_new: int,
    sample_log: list[dict[str, Any]],
    prompt_version: str = "sheet",
) -> dict[str, Any]:
    """Code one row. Handles single-prompt or per-dimension prompts, greedy or voted."""
    voting = num_samples > 1
    result = blank_result(uid)
    notes: list[str] = []
    vote_counts: dict[str, dict[int, int]] = {}

    if not perdim:
        msgs = build_messages(uid=uid, sentences=sentences, exemplars=exemplars or None, prompt_version=prompt_version, **meta)
        raws = _generate(bundle, msgs, max_new, temperature, num_samples=num_samples, top_p=top_p)
        parsed: list[dict[str, Any]] = []
        for i, raw in enumerate(raws):
            res, err = _parse_full(raw, uid)
            sample_log.append({"uid": uid, "dimension": "all", "sample": i, "ok": res is not None,
                               "scores": res["scores"] if res else None,
                               "evidence": res["evidence"] if res else None,
                               "error": err or None, "raw": raw if res is None else None})
            if res is not None:
                parsed.append(res)
        if not parsed:
            last_err = sample_log[-1].get("error") if sample_log else ""
            result["notes"] = last_err if len(raws) == 1 else f"parse_error: all {len(raws)} samples failed; last: {last_err}"
            return result
        if not voting:
            return parsed[0]
        for d in SCORE_DIMS:
            win, counts = _vote([p["scores"][d] for p in parsed])
            vote_counts[d] = counts
            result["scores"][d] = win
            src = next((p for p in parsed if p["scores"][d] == win), None)
            result["evidence"][d] = list(src["evidence"].get(d) or []) if (src and win > 0) else []
        notes.append(f"vote over {len(parsed)}/{len(raws)} parsed samples")
        first = next((p for p in parsed if p.get("notes")), None)
        if first:
            notes.append(str(first["notes"]))
    else:
        for d in SCORE_DIMS:
            msgs = build_perdim_messages(dim=d, uid=uid, sentences=sentences, prompt_version=prompt_version, **meta)
            raws = _generate(bundle, msgs, max_new, temperature, num_samples=num_samples, top_p=top_p)
            parsed_d: list[tuple[int, list[str], str]] = []
            for i, raw in enumerate(raws):
                res, err = _parse_perdim(raw, d)
                sample_log.append({"uid": uid, "dimension": d, "sample": i, "ok": res is not None,
                                   "score": res[0] if res else None,
                                   "evidence": res[1] if res else None,
                                   "error": err or None, "raw": raw if res is None else None})
                if res is not None:
                    parsed_d.append(res)
            if not parsed_d:
                notes.append(f"{d}: parse_error on all {len(raws)} samples")
                continue
            win, counts = _vote([p[0] for p in parsed_d])
            if voting:
                vote_counts[d] = counts
            result["scores"][d] = win
            src = next((p for p in parsed_d if p[0] == win), None)
            result["evidence"][d] = list(src[1]) if (src and win > 0) else []
            if src and src[2]:
                notes.append(f"{d}: {src[2]}")
    result["notes"] = " || ".join(n for n in notes if n)
    if vote_counts:
        result["vote_counts"] = {d: {str(k): v for k, v in c.items()} for d, c in vote_counts.items()}
    return result


def _row_text(row, key: str) -> str:
    """String cell, or empty if the column or value is missing. NaN-safe."""
    if key not in row.index:
        return ""
    val = row[key]
    try:
        import pandas as pd
        if pd.isna(val):
            return ""
    except (TypeError, ValueError):
        if val is None:
            return ""
    s = str(val).strip()
    return "" if s.lower() == "nan" else s


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
    parser.add_argument(
        "--prompt-mode",
        choices=["single", "perdim"],
        default="single",
        help="single = one prompt scores all four dimensions (original); perdim = one prompt per dimension",
    )
    parser.add_argument("--prompt-version", choices=["sheet", "v3", "v4"], default="sheet", help="sheet = sheet-aligned prompt (baseline); v3 = fix3 rubric; v4 = v3 with the sheet-aligned applied rule")
    parser.add_argument("--num-samples", type=int, default=1, help="Samples per prompt; >1 enables majority vote")
    parser.add_argument("--sample-temperature", type=float, default=0.7, help="Temperature used when --num-samples > 1")
    parser.add_argument("--top-p", type=float, default=0.95, help="top_p used when --num-samples > 1")
    parser.add_argument("--max-new-tokens", type=int, default=None, help="Override model.max_new_tokens from config")
    parser.add_argument("--output-samples-jsonl", type=Path, default=None, help="Write every sample (for vote inspection)")
    args = parser.parse_args(argv)

    cfg = _load_config(args.config)
    paths = cfg.get("paths") or {}
    model_cfg = cfg.get("model") or {}
    inf_cfg = cfg.get("inference") or {}

    cache = args.hf_cache or paths.get("hf_cache") or os.environ.get("HF_HOME")
    _set_hf_cache(cache)

    seed = args.seed if args.seed is not None else int(cfg.get("seed", 42))
    csv_path = args.csv or Path(paths.get("data_csv", "data/coding.csv"))
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
    max_new = int(args.max_new_tokens or model_cfg.get("max_new_tokens", 1024))
    num_samples = max(1, int(args.num_samples or 1))
    perdim = args.prompt_mode == "perdim"
    if perdim and exemplars:
        print("ERROR: --prompt-mode perdim does not support few-shot exemplars", file=sys.stderr)
        return 1
    if num_samples > 1:
        temperature = float(args.sample_temperature)
        top_p: float | None = float(args.top_p)
        if temperature <= 0:
            print("ERROR: --num-samples > 1 needs --sample-temperature > 0", file=sys.stderr)
            return 1
    else:
        temperature = float(model_cfg.get("temperature", 0.0))
        top_p = None
    print(f"[info] prompt_version={args.prompt_version} prompt_mode={args.prompt_mode} num_samples={num_samples} temperature={temperature} top_p={top_p} max_new_tokens={max_new} n_rows={len(df)}", flush=True)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass

    sample_log: list[dict[str, Any]] = []
    import time
    t0 = time.time()
    for i_row, (_, row) in enumerate(df.iterrows()):
        uid = str(row.get("uid", ""))
        sentences = str(row.get(text_col, "") or "")
        executive = _row_text(row, "executive")
        # call_title substitutes when company (and the other call metadata) are absent.
        company = _row_text(row, "company") or _row_text(row, "call_title")
        call_date = _row_text(row, "call_date")
        if dry_run or bundle is None:
            result = _mock_code_row(uid, sentences)
        else:
            result = _code_row(
                bundle,
                uid=uid,
                meta={"executive": executive, "company": company, "call_date": call_date},
                sentences=sentences,
                exemplars=exemplars or None,
                perdim=perdim,
                num_samples=num_samples,
                temperature=temperature,
                top_p=top_p,
                max_new=max_new,
                sample_log=sample_log,
                prompt_version=args.prompt_version,
            )

        errs = validate_result(result, require_evidence_for_nonzero=False)
        result["validation_warnings"] = errs
        results.append(result)
        el = time.time() - t0
        print(f"coded uid={uid} scores={result['scores']} votes={result.get('vote_counts', '')} [{i_row + 1}/{len(df)} {el / 60:.1f} min]", flush=True)

    if args.output_samples_jsonl is not None:
        args.output_samples_jsonl.parent.mkdir(parents=True, exist_ok=True)
        with args.output_samples_jsonl.open("w") as f:
            for rec in sample_log:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        print(f"wrote {args.output_samples_jsonl} ({len(sample_log)} samples)")

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
