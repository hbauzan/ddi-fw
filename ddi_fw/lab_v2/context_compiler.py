"""Compilador determinista de historiales largos hacia un presupuesto de tokens."""

from __future__ import annotations

import ast
import re
from collections import Counter
from dataclasses import dataclass

import numpy as np

from ddi_fw.lab_v2.ast_symbol_index import LiveSymbolIndex, extract_python_blocks

_PY_FENCE = re.compile(r"```python\n(.*?)```", re.DOTALL)
_ERROR_LINE = re.compile(r"^[A-Za-z_][\w.]*Error\b|^[A-Za-z_][\w.]*Exception\b")


@dataclass(frozen=True)
class CompiledContextResult:
    messages: list[dict[str, str]]
    original_tokens: int
    compiled_tokens: int
    compression_ratio: float
    superseded_blocks_pruned: int
    stale_traces_pruned: int


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    return max(1, (len(text) + 3) // 4)


def compile_session_context(
    messages: list[dict[str, str]],
    *,
    symbol_index: LiveSymbolIndex | None = None,
    negative_memory: list[object] | None = None,
    turn_vectors: np.ndarray | None = None,
    query_vector: np.ndarray | None = None,
    max_budget_tokens: int = 36000,
    fresh_tail_turns: int = 6,
    force_hygiene: bool = False,
    whiten_mean: np.ndarray | None = None,
    whiten_matrix: np.ndarray | None = None,
) -> CompiledContextResult:
    if max_budget_tokens < 1 or fresh_tail_turns < 0:
        raise ValueError("presupuesto o cola inválidos")
    original_tokens = sum(estimate_tokens(message.get("content", "")) for message in messages)
    if original_tokens <= max_budget_tokens and not force_hygiene:
        copied = [dict(message) for message in messages]
        return CompiledContextResult(
            messages=copied,
            original_tokens=original_tokens,
            compiled_tokens=original_tokens,
            compression_ratio=1.0 if original_tokens == 0 else 1.0,
            superseded_blocks_pruned=0,
            stale_traces_pruned=0,
        )
    index = symbol_index if symbol_index is not None else _index_from_messages(messages)
    notes = list(negative_memory or [])
    last_def = _last_definition_index(messages)
    head, intermediate, tail = _partition(messages, fresh_tail_turns)
    pruned_blocks = 0
    pruned_traces = 0
    hygienic: list[tuple[int, dict[str, str]]] = []
    for index_in_source, message in intermediate:
        content, blocks, traces = _hygiene(message.get("content", ""), index_in_source, last_def)
        pruned_blocks += blocks
        pruned_traces += traces
        hygienic.append((index_in_source, {"role": message.get("role", "user"), "content": content}))
    governor = {
        "role": "system",
        "content": _governor_text(index, notes),
    }
    query = _query_text(messages)
    ranked = sorted(
        hygienic,
        key=lambda item: (
            -_similarity(
                item[1]["content"],
                query,
                item[0],
                turn_vectors,
                query_vector,
                whiten_mean,
                whiten_matrix,
            ),
            item[0],
        ),
    )
    selected: list[tuple[int, dict[str, str]]] = []
    base_messages = [dict(message) for _index, message in head]
    base_messages.append(governor)
    base_messages.extend(dict(message) for _index, message in tail)
    used = sum(estimate_tokens(message["content"]) for message in base_messages)
    for source_index, message in ranked:
        cost = estimate_tokens(message["content"])
        if used + cost <= max_budget_tokens:
            selected.append((source_index, message))
            used += cost
    selected.sort(key=lambda item: item[0])
    compiled = [dict(message) for _index, message in head]
    compiled.append(governor)
    compiled.extend(message for _index, message in selected)
    compiled.extend(dict(message) for _index, message in tail)
    compiled_tokens = sum(estimate_tokens(message["content"]) for message in compiled)
    ratio = 1.0 if original_tokens == 0 else float(compiled_tokens) / float(original_tokens)
    return CompiledContextResult(
        messages=compiled,
        original_tokens=original_tokens,
        compiled_tokens=compiled_tokens,
        compression_ratio=ratio,
        superseded_blocks_pruned=pruned_blocks,
        stale_traces_pruned=pruned_traces,
    )


def _partition(
    messages: list[dict[str, str]],
    fresh_tail_turns: int,
) -> tuple[list[tuple[int, dict[str, str]]], list[tuple[int, dict[str, str]]], list[tuple[int, dict[str, str]]]]:
    first_user = next((index for index, message in enumerate(messages) if message.get("role") == "user"), None)
    head_ids = {
        index
        for index, message in enumerate(messages)
        if message.get("role") == "system" or index == first_user
    }
    tail_start = max(0, len(messages) - fresh_tail_turns)
    tail_ids = set(range(tail_start, len(messages))) - head_ids
    head = [(index, messages[index]) for index in range(len(messages)) if index in head_ids]
    intermediate = [
        (index, messages[index])
        for index in range(len(messages))
        if index not in head_ids and index not in tail_ids
    ]
    tail = [(index, messages[index]) for index in range(len(messages)) if index in tail_ids]
    return head, intermediate, tail


def _last_definition_index(messages: list[dict[str, str]]) -> dict[str, int]:
    last: dict[str, int] = {}
    for index, message in enumerate(messages):
        content = message.get("content", "")
        if "```python\n" not in content and not content.lstrip().startswith(("def ", "class ", "async def", "@")):
            continue
        for block in extract_python_blocks(content):
            for name in _defined_names(block):
                last[name] = index
    return last


def _defined_names(code: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return []
    names: list[str] = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            names.append(node.name)
        elif isinstance(node, ast.ClassDef):
            names.append(node.name)
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.append(f"{node.name}.{sub.name}")
    return names


def _hygiene(content: str, message_index: int, last_def: dict[str, int]) -> tuple[str, int, int]:
    if "```" not in content and "Traceback (most recent call last):" not in content:
        return content, 0, 0
    pruned_blocks = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal pruned_blocks
        names = _defined_names(match.group(1))
        superseded = [name for name in names if last_def.get(name, message_index) > message_index]
        if not superseded:
            return match.group(0)
        pruned_blocks += 1
        joined = ", ".join(superseded)
        return f"[DDI-TOMBSTONE: versión obsoleta de {joined} reemplazada en turno posterior]"

    rewritten = _PY_FENCE.sub(replace, content)
    truncated, pruned_traces = _truncate_traces(rewritten)
    return truncated, pruned_blocks, pruned_traces


def _truncate_traces(content: str) -> tuple[str, int]:
    if "Traceback (most recent call last):" not in content:
        return content, 0
    lines = content.splitlines()
    output: list[str] = []
    pruned = 0
    index = 0
    while index < len(lines):
        if lines[index].startswith("Traceback (most recent call last):"):
            end = index + 1
            while end < len(lines) and (
                lines[end].startswith((" ", "\t", "File "))
            ):
                end += 1
            if end < len(lines) and _ERROR_LINE.match(lines[end]):
                end += 1
            block = lines[index:end]
            if len(block) > 5:
                last = next((line for line in reversed(block) if line.strip()), block[-1])
                output.append(last)
                pruned += 1
            else:
                output.extend(block)
            index = end
        else:
            output.append(lines[index])
            index += 1
    return "\n".join(output), pruned


def _governor_text(index: LiveSymbolIndex, notes: list[object]) -> str:
    lines = ["[DDI-CONTEXT-GOVERNOR]", "Firmas vivas:"]
    if not index.live_signatures:
        lines.append("- (ninguna)")
    for qualname in sorted(index.live_signatures):
        lines.append(f"- {index.render_signature(index.live_signatures[qualname])}")
    lines.append("Firmas deprecadas prohibidas:")
    if not index.deprecated_history:
        lines.append("- (ninguna)")
    for qualname in sorted(index.deprecated_history):
        for old in index.deprecated_history[qualname]:
            lines.append(
                f"- prohibida {index.render_signature(old)} desde el turno {old.turn_id}"
            )
    lines.append("Memoria negativa reciente:")
    recent = notes[-8:]
    if not recent:
        lines.append("- (ninguna)")
    for note in recent:
        turn_id = getattr(note, "turn_id", "?")
        reason = getattr(note, "reason", "")
        lines.append(f"- turno {turn_id}: {reason}")
    return "\n".join(lines)


def _index_from_messages(messages: list[dict[str, str]]) -> LiveSymbolIndex:
    index = LiveSymbolIndex()
    for position, message in enumerate(messages):
        blocks = extract_python_blocks(message.get("content", ""))
        if blocks:
            index.ingest_accepted_turn(position, blocks)
    return index


def _query_text(messages: list[dict[str, str]]) -> str:
    for message in reversed(messages):
        if message.get("role") == "user":
            return message.get("content", "")
    return messages[-1].get("content", "") if messages else ""


def _similarity(
    content: str,
    query: str,
    message_index: int,
    turn_vectors: np.ndarray | None,
    query_vector: np.ndarray | None,
    whiten_mean: np.ndarray | None,
    whiten_matrix: np.ndarray | None,
) -> float:
    if (
        turn_vectors is not None
        and query_vector is not None
        and 0 <= message_index < len(turn_vectors)
    ):
        return _whitened_cosine(
            np.asarray(turn_vectors[message_index], dtype=np.float64),
            np.asarray(query_vector, dtype=np.float64),
            whiten_mean,
            whiten_matrix,
        )
    return _lexical_cosine(content, query)


def _whitened_cosine(
    vector: np.ndarray,
    query: np.ndarray,
    whiten_mean: np.ndarray | None,
    whiten_matrix: np.ndarray | None,
) -> float:
    mean = np.zeros(vector.shape[0], dtype=np.float64) if whiten_mean is None else whiten_mean
    if whiten_matrix is None:
        left = vector - mean
        right = query - mean
    else:
        left = whiten_matrix @ (vector - mean)
        right = whiten_matrix @ (query - mean)
    denom = float(np.linalg.norm(left) * np.linalg.norm(right)) + 1e-12
    return float(np.dot(left, right) / denom)


def _lexical_cosine(content: str, query: str) -> float:
    left = Counter(_words(content))
    right = Counter(_words(query))
    if not left or not right:
        return 0.0
    shared = set(left) & set(right)
    dot = float(sum(left[token] * right[token] for token in shared))
    left_norm = float(sum(value * value for value in left.values())) ** 0.5
    right_norm = float(sum(value * value for value in right.values())) ** 0.5
    return dot / (left_norm * right_norm + 1e-12)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9_]+", text.lower())
