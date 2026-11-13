"""Índice vivo de firmas Python y huella estructural anti-clones."""

from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass

_PY_FENCE = re.compile(r"```python\n(.*?)```", re.DOTALL)


@dataclass(frozen=True)
class FunctionSig:
    qualname: str
    min_pos_args: int
    max_pos_args: int | None
    required_kwonly: frozenset[str]
    allowed_kwargs: frozenset[str] | None
    turn_id: int
    pos_names: tuple[str, ...] = ()
    kwonly_names: tuple[str, ...] = ()
    typed_signature: str = ""


@dataclass(frozen=True)
class AstViolation:
    kind: str
    symbol: str
    detail: str
    deprecated_from_turn: int | None = None


def extract_python_blocks(message_text: str) -> list[str]:
    """Extrae cercas ```python``` o el texto entero si es Python ejecutable."""
    if not message_text or not message_text.strip():
        return []
    fenced = [block for block in _PY_FENCE.findall(message_text) if block.strip()]
    if fenced:
        return fenced
    if len(message_text) > 20000 and "```python\n" not in message_text:
        return []
    try:
        tree = ast.parse(message_text)
    except SyntaxError:
        return []
    if not tree.body:
        return []
    return [message_text]


def compute_structural_ast_hash(code: str) -> str | None:
    """Hash SHA-256 del AST sin docstrings, comentarios ni nombres locales."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    _strip_docstrings(tree)
    _canonicalize(tree)
    payload = ast.dump(tree, annotate_fields=True, include_attributes=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class LiveSymbolIndex:
    """Firmas aceptadas, historia deprecada y métodos de clases locales."""

    def __init__(self) -> None:
        self.live_signatures: dict[str, FunctionSig] = {}
        self.deprecated_history: dict[str, list[FunctionSig]] = {}
        self.class_methods: dict[str, set[str]] = {}

    def ingest_accepted_turn(self, turn_id: int, code_blocks: list[str]) -> None:
        for block in code_blocks:
            try:
                tree = ast.parse(block)
            except SyntaxError:
                continue
            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    self._store_function(node.name, node, turn_id, is_method=False)
                elif isinstance(node, ast.ClassDef):
                    methods: set[str] = set()
                    for sub in node.body:
                        if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods.add(sub.name)
                            self._store_function(
                                f"{node.name}.{sub.name}",
                                sub,
                                turn_id,
                                is_method=True,
                            )
                    self.class_methods[node.name] = methods

    def audit_candidate_code(self, code: str) -> list[AstViolation]:
        try:
            tree = ast.parse(code)
        except SyntaxError as exc:
            return [
                AstViolation(
                    kind="syntax_error",
                    symbol="<module>",
                    detail=f"SyntaxError: {exc.msg}",
                )
            ]
        auditor = _CallAuditor(self)
        auditor.visit(tree)
        return auditor.violations

    def render_signature(self, sig: FunctionSig) -> str:
        parts = list(sig.pos_names)
        if sig.kwonly_names:
            parts.append("*")
            parts.extend(sig.kwonly_names)
        return f"{sig.qualname}({', '.join(parts)})"

    def render_typed_signature(self, sig: FunctionSig) -> str:
        return sig.typed_signature or self.render_signature(sig)

    def find_deprecated_calls(self, code: str) -> list[AstViolation]:
        return [
            violation
            for violation in self.audit_candidate_code(code)
            if violation.kind == "deprecated_signature_call"
        ]

    def _store_function(
        self,
        qualname: str,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
        turn_id: int,
        *,
        is_method: bool,
    ) -> None:
        fresh = _build_signature(qualname, node, turn_id, is_method=is_method)
        current = self.live_signatures.get(qualname)
        if current is not None and not _same_contract(current, fresh):
            self.deprecated_history.setdefault(qualname, []).append(current)
        self.live_signatures[qualname] = fresh

    def _check_named_call(self, name: str, call: ast.Call, violations: list[AstViolation]) -> None:
        live = self.live_signatures.get(name)
        if live is None:
            return
        if _call_matches(live, call):
            return
        for old in reversed(self.deprecated_history.get(name, [])):
            if _call_matches(old, call):
                violations.append(
                    AstViolation(
                        kind="deprecated_signature_call",
                        symbol=name,
                        detail=(
                            f"{name} coincide con la firma del turno {old.turn_id} "
                            f"y no con la firma viva"
                        ),
                        deprecated_from_turn=old.turn_id,
                    )
                )
                return
        violations.append(
            AstViolation(
                kind="arity_mismatch",
                symbol=name,
                detail=f"{name} no entra en la firma viva ni en una firma deprecada",
            )
        )


class _CallAuditor(ast.NodeVisitor):
    def __init__(self, index: LiveSymbolIndex) -> None:
        self.index = index
        self.instances: dict[str, str] = {}
        self.violations: list[AstViolation] = []

    def visit_Assign(self, node: ast.Assign) -> None:
        self.visit(node.value)
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in self.index.class_methods
        ):
            self.instances[node.targets[0].id] = node.value.func.id
        for target in node.targets:
            self.visit(target)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        if node.value is not None:
            self.visit(node.value)
        if (
            isinstance(node.target, ast.Name)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Name)
            and node.value.func.id in self.index.class_methods
        ):
            self.instances[node.target.id] = node.value.func.id

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        if isinstance(func, ast.Name):
            self.index._check_named_call(func.id, node, self.violations)
        elif isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            class_name = self.instances.get(func.value.id)
            if class_name is not None and func.attr not in self.index.class_methods.get(class_name, set()):
                self.violations.append(
                    AstViolation(
                        kind="unknown_class_method",
                        symbol=f"{class_name}.{func.attr}",
                        detail=f"{func.value.id}.{func.attr} no pertenece a {class_name}",
                    )
                )
        self.generic_visit(node)


def _build_signature(
    qualname: str,
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    turn_id: int,
    *,
    is_method: bool,
) -> FunctionSig:
    args = node.args
    positional = [*args.posonlyargs, *args.args]
    if is_method and positional and positional[0].arg in {"self", "cls"}:
        positional = positional[1:]
    defaulted: set[str] = set()
    if args.defaults:
        original = [*args.posonlyargs, *args.args]
        for arg in original[-len(args.defaults) :]:
            defaulted.add(arg.arg)
    pos_names = tuple(arg.arg for arg in positional)
    min_pos = sum(1 for name in pos_names if name not in defaulted)
    max_pos = None if args.vararg is not None else len(pos_names)
    required_kwonly = frozenset(
        arg.arg for arg, default in zip(args.kwonlyargs, args.kw_defaults, strict=False) if default is None
    )
    if args.kwarg is not None:
        allowed: frozenset[str] | None = None
    else:
        allowed = frozenset(pos_names) | frozenset(arg.arg for arg in args.kwonlyargs)
    return FunctionSig(
        qualname=qualname,
        min_pos_args=min_pos,
        max_pos_args=max_pos,
        required_kwonly=required_kwonly,
        allowed_kwargs=allowed,
        turn_id=turn_id,
        pos_names=pos_names,
        kwonly_names=tuple(arg.arg for arg in args.kwonlyargs),
        typed_signature=_typed_signature_text(qualname, node),
    )


def _typed_signature_text(qualname: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    rendered = f"{qualname}({ast.unparse(node.args)})"
    if node.returns is not None:
        return f"{rendered} -> {ast.unparse(node.returns)}"
    return rendered


def _same_contract(left: FunctionSig, right: FunctionSig) -> bool:
    return (
        left.min_pos_args == right.min_pos_args
        and left.max_pos_args == right.max_pos_args
        and left.required_kwonly == right.required_kwonly
        and left.allowed_kwargs == right.allowed_kwargs
    )


def _call_matches(sig: FunctionSig, call: ast.Call) -> bool:
    if any(isinstance(arg, ast.Starred) for arg in call.args):
        return True
    if any(keyword.arg is None for keyword in call.keywords):
        return True
    kw_names = [keyword.arg for keyword in call.keywords if keyword.arg is not None]
    if sig.allowed_kwargs is not None and any(name not in sig.allowed_kwargs for name in kw_names):
        return False
    positional_by_name = set(sig.pos_names)
    keyword_positionals = [name for name in kw_names if name in positional_by_name]
    if len(call.args) + len(keyword_positionals) < sig.min_pos_args:
        return False
    if sig.max_pos_args is not None and len(call.args) > sig.max_pos_args:
        return False
    if sig.required_kwonly - set(kw_names):
        return False
    return True


def _strip_docstrings(node: ast.AST) -> None:
    if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        body = getattr(node, "body", None)
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            del body[0]
    for child in ast.iter_child_nodes(node):
        _strip_docstrings(child)


def _canonicalize(node: ast.AST) -> None:
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        _rename_locals_shallow(node)
    for child in list(ast.iter_child_nodes(node)):
        _canonicalize(child)


def _rename_locals_shallow(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
    mapping: dict[str, str] = {}
    counter = 0

    def bind(name: str) -> None:
        nonlocal counter
        if name not in mapping:
            mapping[name] = f"v{counter}"
            counter += 1

    args = fn.args
    for arg in [*args.posonlyargs, *args.args, *args.kwonlyargs]:
        bind(arg.arg)
    if args.vararg is not None:
        bind(args.vararg.arg)
    if args.kwarg is not None:
        bind(args.kwarg.arg)

    def collect(tree: ast.AST) -> None:
        for child in ast.iter_child_nodes(tree):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    bind(child.name)
                continue
            if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store):
                bind(child.id)
            collect(child)

    for stmt in fn.body:
        collect(stmt)

    def apply_node(tree: ast.AST) -> None:
        if isinstance(tree, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)):
            if isinstance(tree, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and tree.name in mapping:
                tree.name = mapping[tree.name]
            return
        if isinstance(tree, ast.Name) and tree.id in mapping:
            tree.id = mapping[tree.id]
        elif isinstance(tree, ast.arg) and tree.arg in mapping:
            tree.arg = mapping[tree.arg]
        for child in ast.iter_child_nodes(tree):
            apply_node(child)

    for arg in [*args.posonlyargs, *args.args, *args.kwonlyargs]:
        arg.arg = mapping[arg.arg]
    if args.vararg is not None:
        args.vararg.arg = mapping[args.vararg.arg]
    if args.kwarg is not None:
        args.kwarg.arg = mapping[args.kwarg.arg]
    for default in [*args.defaults, *args.kw_defaults]:
        if default is not None:
            apply_node(default)
    for stmt in fn.body:
        apply_node(stmt)
