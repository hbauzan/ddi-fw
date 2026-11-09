"""Punto de entrada del Test B. `--live-api` queda bloqueado."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from ddi_fw.embedder import get_embedder
from ddi_fw.hardware import get_hardware_profile
from ddi_fw.lab_v2.session_eval import embed_signal_matrices, evaluate_sessions
from ddi_fw.lab_v2.session_metrics import render_test_b_markdown
from ddi_fw.lab_v2.session_simulator import build_benchmark_sessions, load_external_jsonl_sessions

_DEFAULT_JSON = Path("reports/lab_v2_test_b_results.json")
_DEFAULT_MD = Path("reports/test_b_context_rot_250k.md")


def run_test_b(
    *,
    embedder_name: str,
    json_path: Path,
    md_path: Path,
    target_tokens: int = 265_000,
    seed: int = 42,
    transcripts_dir: Path | None = None,
    live_api: bool = False,
    batch_size: int = 32,
) -> dict[str, object]:
    if live_api:
        raise RuntimeError("TASK-003 está bloqueada: no se llama ninguna API viva")
    sessions = build_benchmark_sessions(seed=seed, target_tokens=target_tokens)
    if transcripts_dir is not None:
        sessions.extend(load_external_jsonl_sessions(transcripts_dir))
    embedder = _load_embedder(embedder_name)
    matrices = embed_signal_matrices(sessions, embedder, batch_size=batch_size)
    measured = evaluate_sessions(sessions, matrices)
    payload: dict[str, object] = {
        "task_id": "TASK-002",
        "embedder": embedder.model_id,
        "target_tokens": target_tokens,
        "n_sessions": len(sessions),
        "token_range": {
            "min": min(session.total_tokens for session in sessions),
            "max": max(session.total_tokens for session in sessions),
        },
        "detectors": measured["detectors"],
        "compiler": measured["compiler"],
        "verdict": measured["verdict"],
        "hardware": get_hardware_profile(),
    }
    _write_outputs(payload, json_path, md_path)
    return payload


def main(argv: list[str] | None = None) -> dict[str, object]:
    parser = argparse.ArgumentParser(description="Context rot y compilador del Test B")
    parser.add_argument("--embedder", default="bge", choices=("bge", "fake"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--target-tokens", type=int, default=265_000)
    parser.add_argument("--json-out", type=Path, default=_DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=_DEFAULT_MD)
    parser.add_argument("--transcripts-dir", type=Path, default=None)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--live-api", action="store_true")
    args = parser.parse_args(argv)
    return run_test_b(
        embedder_name=args.embedder,
        json_path=args.json_out,
        md_path=args.md_out,
        target_tokens=args.target_tokens,
        seed=args.seed,
        transcripts_dir=args.transcripts_dir,
        live_api=bool(args.live_api),
        batch_size=args.batch_size,
    )


def _load_embedder(name: str) -> object:
    key = name.strip().casefold()
    if key == "bge":
        return get_embedder("BAAI/bge-m3")
    if key == "fake":
        return get_embedder("fake")
    return get_embedder(name)


def _write_outputs(payload: dict[str, object], json_path: Path, md_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(_jsonable(payload), indent=2, ensure_ascii=False, allow_nan=False)
    json_path.write_text(encoded + "\n", encoding="utf-8")
    md_path.write_text(render_test_b_markdown(payload), encoding="utf-8")


def _jsonable(value: object) -> object:
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.integer) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, np.bool_):
        return bool(value)
    return value


if __name__ == "__main__":
    main()
