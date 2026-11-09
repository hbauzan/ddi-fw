"""Segmentador estructural: AST de Python y ventanas, sin líneas huérfanas."""

from __future__ import annotations

import ast
import io
import re
import tokenize
from dataclasses import dataclass
from typing import Literal

ChunkKind = Literal["python_ast", "fenced_code", "foreign_code", "prose_window"]

_FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)
_BASH_SHEBANG_RE = re.compile(r"(?m)^#!\s*/(?:usr/bin/env\s+)?(?:ba|z|da|k)?sh\b")
_BASH_SET_RE = re.compile(r"(?m)^\s*set\s+-[euo]+")
_BASH_CASE_RE = re.compile(r"(?s)\bcase\s+.+\bin\b.+\besac\b")
_BASH_LOOP_RE = re.compile(r"(?s)\b(?:for|while)\b.+;\s*do\b.+\bdone\b")
_SQL_DDL_RE = re.compile(
    r"(?is)^\s*(?:CREATE\s+(?:TABLE|VIEW|(?:UNIQUE\s+)?INDEX)|INSERT\s+INTO|"
    r"UPDATE\s+\w+\s+SET|DELETE\s+FROM|ALTER\s+TABLE|DROP\s+(?:TABLE|VIEW|INDEX))\b"
)
_SQL_SELECT_UPPER_RE = re.compile(r"\bSELECT\b[\s\S]+\bFROM\b")
_SQL_SELECT_STRUCT_RE = re.compile(
    r"(?is)^\s*select\b[\s\S]+\bfrom\b[\s\S]*(?:;\s*$|\b(?:where|group\s+by|order\s+by|having|join)\b)"
)
_JS_FUNC_RE = re.compile(r"(?m)^\s*(?:export\s+)?(?:async\s+)?function\s+[A-Za-z_$][\w$]*\s*\(")
_JS_DECL_RE = re.compile(r"\b(?:const|let|var)\s+[A-Za-z_$][\w$]*\s*=")
_JS_BRACE_RE = re.compile(r"\{[\s\S]*\}")
_RUST_FN_RE = re.compile(r"(?m)^\s*(?:pub\s+)?fn\s+[A-Za-z_]\w*\s*\([^)]*\)\s*(?:->\s*[^\{]+)?\{")
_RUST_STRUCT_RE = re.compile(r"(?m)^\s*(?:pub\s+)?struct\s+[A-Za-z_]\w*\s*\{")
_C_INCLUDE_RE = re.compile(r"""(?m)^\s*#include\s*[<"][^>"]+[>"]""")
_C_FUNC_RE = re.compile(
    r"(?ms)^\s*(?:static\s+|inline\s+|unsigned\s+|const\s+)*"
    r"(?:void|int|long|float|double|char|bool|size_t|ssize_t|uint\d+_t|int\d+_t)"
    r"\s+\*?\s*[A-Za-z_]\w*\s*\([^;{}]*\)\s*\{[\s\S]*;[\s\S]*\}"
)
_GO_PACKAGE_RE = re.compile(r"(?m)^\s*package\s+[A-Za-z_]\w*\s*$")
_GO_FUNC_RE = re.compile(r"(?m)^\s*func\s+(?:\([^)]+\)\s*)?[A-Za-z_]\w*\s*\(")
_SENTENCE_RE = re.compile(r"(?<=[.!?])\s+|\n{2,}")
_SIMPLE_NODES = (ast.Import, ast.ImportFrom, ast.Assign, ast.AnnAssign, ast.Expr)
_MIN_PROSE_CHARS = 40
_MIN_FRAGMENT_CHARS = 4


@dataclass(frozen=True)
class TextChunk:
    text: str
    kind: ChunkKind
    is_valid_python_ast: bool
    start_line: int
    end_line: int


def extract_chunks(
    text: str,
    max_ast_lines: int = 30,
    window_lines: int = 12,
    stride_lines: int = 6,
) -> list[TextChunk]:
    """Parte `text` en bloques con contexto. Nunca devuelve un `else:` suelto."""
    if not text or not text.strip():
        return []
    if max_ast_lines < 1 or window_lines < 1 or stride_lines < 1:
        raise ValueError("max_ast_lines, window_lines y stride_lines deben ser >= 1")
    fences = list(_FENCE_RE.finditer(text))
    if fences:
        return _chunks_from_fenced_document(
            text,
            fences,
            max_ast_lines=max_ast_lines,
            window_lines=window_lines,
            stride_lines=stride_lines,
        )
    if _is_executable_python(text):
        return _chunks_from_python(
            text,
            base_line=1,
            max_ast_lines=max_ast_lines,
            window_lines=window_lines,
            stride_lines=stride_lines,
        )
    return _chunks_from_non_python(
        text,
        base_line=1,
        window_lines=window_lines,
        stride_lines=stride_lines,
    )


def _is_executable_python(code: str) -> bool:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return False
    if not tree.body:
        return False
    if (
        len(tree.body) == 1
        and isinstance(tree.body[0], ast.Expr)
        and isinstance(getattr(tree.body[0], "value", None), ast.Constant)
    ):
        return False
    return True


def _chunks_from_fenced_document(
    text: str,
    fences: list[re.Match[str]],
    *,
    max_ast_lines: int,
    window_lines: int,
    stride_lines: int,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    cursor = 0
    for match in fences:
        before = text[cursor : match.start()]
        if before.strip():
            base = text.count("\n", 0, cursor) + 1
            chunks.extend(
                _chunks_from_non_python(
                    before,
                    base_line=base,
                    window_lines=window_lines,
                    stride_lines=stride_lines,
                )
            )
        code = match.group(2)
        code_base = text.count("\n", 0, match.start(2)) + 1
        if code.strip() and _is_executable_python(code):
            chunks.extend(
                _chunks_from_python(
                    code,
                    base_line=code_base,
                    max_ast_lines=max_ast_lines,
                    window_lines=window_lines,
                    stride_lines=stride_lines,
                )
            )
        elif code.strip():
            chunks.extend(
                _emit_line_windows(
                    code.splitlines(),
                    abs_start=code_base,
                    kind="fenced_code",
                    is_valid_python_ast=False,
                    max_lines=window_lines,
                    window_lines=window_lines,
                    stride_lines=stride_lines,
                )
            )
        cursor = match.end()
    after = text[cursor:]
    if after.strip():
        chunks.extend(
            _chunks_from_non_python(
                after,
                base_line=text.count("\n", 0, cursor) + 1,
                window_lines=window_lines,
                stride_lines=stride_lines,
            )
        )
    return [chunk for chunk in chunks if chunk.text.strip()]


def _chunks_from_python(
    text: str,
    *,
    base_line: int,
    max_ast_lines: int,
    window_lines: int,
    stride_lines: int,
) -> list[TextChunk]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return _chunks_from_prose(text, base_line=base_line)
    chunks: list[TextChunk] = []
    body = list(tree.body)
    index = 0
    while index < len(body):
        node = body[index]
        if isinstance(node, _SIMPLE_NODES):
            end_index = index + 1
            while end_index < len(body) and isinstance(body[end_index], _SIMPLE_NODES):
                end_index += 1
            group = body[index:end_index]
            if not _only_string_literals(group):
                start = int(group[0].lineno)
                end = int(getattr(group[-1], "end_lineno", None) or start)
                segment_lines = _slice_lines(text, start, end)
                chunks.extend(
                    _emit_line_windows(
                        segment_lines,
                        abs_start=base_line + start - 1,
                        kind="python_ast",
                        is_valid_python_ast=True,
                        max_lines=max_ast_lines,
                        window_lines=window_lines,
                        stride_lines=stride_lines,
                    )
                )
            index = end_index
            continue
        start = int(getattr(node, "lineno", 1) or 1)
        end = int(getattr(node, "end_lineno", None) or start)
        segment_lines = _slice_lines(text, start, end)
        chunks.extend(
            _emit_line_windows(
                segment_lines,
                abs_start=base_line + start - 1,
                kind="python_ast",
                is_valid_python_ast=True,
                max_lines=max_ast_lines,
                window_lines=window_lines,
                stride_lines=stride_lines,
            )
        )
        index += 1
    chunks.extend(_prose_from_python_tree(text, tree, base_line=base_line))
    return [chunk for chunk in chunks if chunk.text.strip()]


def _only_string_literals(nodes: list[ast.stmt]) -> bool:
    if not nodes:
        return False
    for node in nodes:
        if not isinstance(node, ast.Expr):
            return False
        value = getattr(node, "value", None)
        if not isinstance(value, ast.Constant) or not isinstance(value.value, str):
            return False
    return True


def _slice_lines(text: str, start: int, end: int) -> list[str]:
    lines = text.splitlines()
    start_idx = max(0, start - 1)
    end_idx = min(len(lines), end)
    return lines[start_idx:end_idx]


def _emit_line_windows(
    lines: list[str],
    *,
    abs_start: int,
    kind: ChunkKind,
    is_valid_python_ast: bool,
    max_lines: int,
    window_lines: int,
    stride_lines: int,
) -> list[TextChunk]:
    if not lines:
        return []
    total = len(lines)
    if total <= max_lines:
        return [_make_chunk(lines, abs_start, kind, is_valid_python_ast)]
    chunks: list[TextChunk] = []
    cursor = 0
    while cursor < total:
        end = min(cursor + window_lines, total)
        if end < total and (total - end) < _MIN_FRAGMENT_CHARS:
            end = total
        piece = lines[cursor:end]
        text = "\n".join(piece).strip()
        if len(text) < _MIN_FRAGMENT_CHARS and chunks:
            previous = chunks[-1]
            merged = previous.text + "\n" + "\n".join(piece)
            chunks[-1] = TextChunk(
                text=merged,
                kind=kind,
                is_valid_python_ast=is_valid_python_ast,
                start_line=previous.start_line,
                end_line=abs_start + end - 1,
            )
        elif text:
            chunks.append(
                TextChunk(
                    text="\n".join(piece),
                    kind=kind,
                    is_valid_python_ast=is_valid_python_ast,
                    start_line=abs_start + cursor,
                    end_line=abs_start + end - 1,
                )
            )
        if end >= total:
            break
        cursor += stride_lines
    return chunks


def _make_chunk(
    lines: list[str],
    abs_start: int,
    kind: ChunkKind,
    is_valid_python_ast: bool,
) -> TextChunk:
    return TextChunk(
        text="\n".join(lines),
        kind=kind,
        is_valid_python_ast=is_valid_python_ast,
        start_line=abs_start,
        end_line=abs_start + len(lines) - 1,
    )


def _prose_from_python_tree(text: str, tree: ast.AST, *, base_line: int) -> list[TextChunk]:
    found: list[tuple[int, int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            payload = node.value.strip()
            if len(payload) >= _MIN_PROSE_CHARS:
                lineno = int(getattr(node, "lineno", 1) or 1)
                end_lineno = int(getattr(node, "end_lineno", None) or lineno)
                found.append((lineno, end_lineno, payload))
    try:
        reader = io.StringIO(text).readline
        for token in tokenize.generate_tokens(reader):
            if token.type != tokenize.COMMENT:
                continue
            payload = token.string.lstrip("#").strip()
            if len(payload) >= _MIN_PROSE_CHARS:
                found.append((token.start[0], token.end[0], payload))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return _dedupe_prose(found, base_line)
    return _dedupe_prose(found, base_line)


def _dedupe_prose(found: list[tuple[int, int, str]], base_line: int) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    seen: set[str] = set()
    for lineno, end_lineno, payload in found:
        if payload in seen:
            continue
        seen.add(payload)
        chunks.append(
            TextChunk(
                text=payload,
                kind="prose_window",
                is_valid_python_ast=False,
                start_line=base_line + lineno - 1,
                end_line=base_line + end_lineno - 1,
            )
        )
    return chunks


def _looks_like_non_python_code(text: str) -> bool:
    """Firmas inequívocas de código ajeno. El llamador ya descartó Python ejecutable."""
    if (
        _BASH_SHEBANG_RE.search(text)
        or _BASH_SET_RE.search(text)
        or _BASH_CASE_RE.search(text)
        or _BASH_LOOP_RE.search(text)
    ):
        return True
    if _SQL_DDL_RE.search(text) or _SQL_SELECT_UPPER_RE.search(text) or _SQL_SELECT_STRUCT_RE.search(text):
        return True
    if _JS_FUNC_RE.search(text):
        return True
    if _JS_DECL_RE.search(text) and (";" in text or "=>" in text or _JS_BRACE_RE.search(text)):
        return True
    if _RUST_FN_RE.search(text) or _RUST_STRUCT_RE.search(text):
        return True
    if _C_INCLUDE_RE.search(text) or _C_FUNC_RE.search(text):
        return True
    if _GO_PACKAGE_RE.search(text) or _GO_FUNC_RE.search(text):
        return True
    return False


def _chunks_from_non_python(
    text: str,
    *,
    base_line: int,
    window_lines: int,
    stride_lines: int,
) -> list[TextChunk]:
    if not _is_executable_python(text) and _looks_like_non_python_code(text):
        return _emit_line_windows(
            text.splitlines(),
            abs_start=base_line,
            kind="foreign_code",
            is_valid_python_ast=False,
            max_lines=window_lines,
            window_lines=window_lines,
            stride_lines=stride_lines,
        )
    return _chunks_from_prose(text, base_line=base_line)


def _chunks_from_prose(text: str, *, base_line: int) -> list[TextChunk]:
    raw = text.strip()
    if not raw:
        return []
    sentences = _group_sentences(raw)
    if not sentences:
        return []
    groups = (
        sentences
        if len(sentences) == 1
        else [sentences[index] + " " + sentences[index + 1] for index in range(len(sentences) - 1)]
    )
    chunks: list[TextChunk] = []
    cursor = 0
    for group in groups:
        probe = group[:48].strip()
        index = text.find(probe, cursor) if probe else -1
        if index < 0 and probe:
            index = text.find(probe)
        if index < 0:
            start_line = base_line
            end_line = base_line + max(0, text.count("\n"))
        else:
            start_line = base_line + text.count("\n", 0, index)
            end_line = start_line + group.count("\n")
            cursor = index + max(1, len(probe))
        if len(group.strip()) < _MIN_FRAGMENT_CHARS:
            continue
        chunks.append(
            TextChunk(
                text=group.strip(),
                kind="prose_window",
                is_valid_python_ast=False,
                start_line=start_line,
                end_line=max(start_line, end_line),
            )
        )
    return chunks


def _group_sentences(raw: str) -> list[str]:
    parts = [part.strip() for part in _SENTENCE_RE.split(raw) if part and part.strip()]
    sentences: list[str] = []
    pending = ""
    for part in parts:
        if len(part) < _MIN_FRAGMENT_CHARS:
            if sentences:
                sentences[-1] = f"{sentences[-1]} {part}"
            else:
                pending = f"{pending} {part}".strip()
            continue
        if pending:
            part = f"{pending} {part}"
            pending = ""
        sentences.append(part)
    if pending:
        if sentences:
            sentences[-1] = f"{sentences[-1]} {pending}"
        else:
            sentences.append(pending)
    return sentences
