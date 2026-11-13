"""Corpus offline y reproducible del Test A. Splits train/cal/test disjuntos."""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import random
import textwrap
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from ddi_fw.lab_v2.fixtures_code import BUSINESS_FUNCTIONS, FOREIGN_SNIPPETS

SplitName = Literal["train", "cal", "test"]
SampleCategory = Literal[
    "pos_stdlib_python",
    "pos_business_python",
    "neg_seen_domain",
    "neg_unseen_domain_ood",
    "neg_other_language",
    "neg_piggybacking",
]

SEEN_DOMAINS: tuple[str, ...] = ("receta", "legal", "medicina", "astronomia", "finanzas")
OOD_DOMAINS: tuple[str, ...] = ("filosofia", "musica", "geologia", "botanica", "arquitectura")
STDLIB_MODULES: tuple[str, ...] = (
    "collections",
    "json.decoder",
    "json.encoder",
    "pathlib",
    "urllib.parse",
    "statistics",
    "csv",
    "configparser",
    "dataclasses",
    "heapq",
    "bisect",
    "functools",
    "difflib",
    "tarfile",
    "zipfile",
    "asyncio.queues",
    "asyncio.locks",
    "logging",
    "pprint",
    "textwrap",
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "trilingual"
_SPLIT_PAIRS = (("train", "cal"), ("train", "test"), ("cal", "test"))
_BANNED_META_SUBSTRINGS: tuple[str, ...] = (
    "python",
    "cpython",
    "sintactico",
    "sintáctico",
    "ast",
    "docstring",
    "stdlib",
    "pos_stdlib",
    "bloque",
)
_CLEAN_PAYLOADS_PER_DOMAIN = 6


@dataclass(frozen=True)
class BenchmarkSample:
    sample_id: str
    text: str
    is_legitimate_python: bool
    category: SampleCategory
    split: SplitName
    subtag: str


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def assert_no_leakage(samples: list[BenchmarkSample]) -> None:
    """Falla si un id o un texto normalizado cruza train, cal y test."""
    grouped: dict[str, list[BenchmarkSample]] = {"train": [], "cal": [], "test": []}
    seen_ids: set[str] = set()
    for sample in samples:
        if sample.sample_id in seen_ids:
            raise ValueError(f"sample_id duplicado: {sample.sample_id}")
        seen_ids.add(sample.sample_id)
        if sample.split not in grouped:
            raise ValueError(f"split desconocido: {sample.split}")
        grouped[sample.split].append(sample)
    for left_name, right_name in _SPLIT_PAIRS:
        left = grouped[left_name]
        right = grouped[right_name]
        if not {item.sample_id for item in left}.isdisjoint({item.sample_id for item in right}):
            raise ValueError(f"sample_id repetido entre {left_name} y {right_name}")
        left_text = {normalize_text(item.text) for item in left}
        right_text = {normalize_text(item.text) for item in right}
        if not left_text.isdisjoint(right_text):
            overlap = left_text & right_text
            preview = next(iter(overlap))[:80]
            raise ValueError(f"texto normalizado repetido entre {left_name} y {right_name}: {preview}")


def build_test_a_dataset(seed: int = 42) -> list[BenchmarkSample]:
    """Arma el dataset del Test A. `seed` fija el barajado; los textos no salen de la red."""
    rng = random.Random(seed)
    samples: list[BenchmarkSample] = []

    stdlib = _stdlib_records()
    stdlib.sort(key=lambda item: item[0])
    rng.shuffle(stdlib)
    if len(stdlib) < 300:
        raise ValueError(f"stdlib elegible={len(stdlib)} < 300")
    for index, (sample_id, text, subtag) in enumerate(stdlib[:300]):
        samples.append(
            _sample(
                sample_id,
                text,
                True,
                "pos_stdlib_python",
                _positive_split(index, 150, 60),
                subtag,
            )
        )

    business = [
        (f"pos_business_python:{subtag}:{name}", source, subtag)
        for subtag, name, source in BUSINESS_FUNCTIONS
    ]
    business.sort(key=lambda item: item[0])
    rng.shuffle(business)
    if len(business) != 60:
        raise ValueError(f"funciones de negocio={len(business)} != 60")
    for index, (sample_id, text, subtag) in enumerate(business):
        samples.append(
            _sample(
                sample_id,
                text,
                True,
                "pos_business_python",
                _positive_split(index, 30, 12),
                subtag,
            )
        )

    seen_rows: list[tuple[str, str, str]] = []
    clause_tails: list[tuple[str, list[tuple[str, str]]]] = []
    for domain in SEEN_DOMAINS:
        clauses = _load_clauses(domain)
        rng.shuffle(clauses)
        if len(clauses) < 40:
            raise ValueError(f"{domain} tiene {len(clauses)} clausulas < 40")
        clause_tails.append((domain, clauses[40:]))
        for clause_id, text in clauses[:40]:
            seen_rows.append((f"neg_seen_domain:{domain}:{clause_id}", text, domain))
    seen_rows.sort(key=lambda item: item[0])
    rng.shuffle(seen_rows)
    if len(seen_rows) != 200:
        raise ValueError(f"neg_seen_domain={len(seen_rows)} != 200")
    for index, (sample_id, text, subtag) in enumerate(seen_rows):
        split: SplitName = "train" if index < 120 else "test"
        samples.append(_sample(sample_id, text, False, "neg_seen_domain", split, subtag))

    for domain in OOD_DOMAINS:
        clauses = _load_clauses(domain)
        rng.shuffle(clauses)
        if len(clauses) < 30:
            raise ValueError(f"{domain} tiene {len(clauses)} clausulas < 30")
        clause_tails.append((domain, clauses[30:]))
        for clause_id, text in clauses[:30]:
            samples.append(
                _sample(
                    f"neg_unseen_domain_ood:{domain}:{clause_id}",
                    text,
                    False,
                    "neg_unseen_domain_ood",
                    "test",
                    domain,
                )
            )

    if len(FOREIGN_SNIPPETS) != 60:
        raise ValueError(f"snippets ajenos={len(FOREIGN_SNIPPETS)} != 60")
    for subtag, name, source in FOREIGN_SNIPPETS:
        samples.append(
            _sample(
                f"neg_other_language:{subtag}:{name}",
                source,
                False,
                "neg_other_language",
                "test",
                subtag,
            )
        )

    samples.extend(_piggyback_samples(samples, clause_tails))
    _assert_contract(samples)
    assert_no_leakage(samples)
    samples.sort(key=lambda item: item.sample_id)
    return samples


def _sample(
    sample_id: str,
    text: str,
    legitimate: bool,
    category: SampleCategory,
    split: SplitName,
    subtag: str,
) -> BenchmarkSample:
    return BenchmarkSample(
        sample_id=sample_id,
        text=text,
        is_legitimate_python=legitimate,
        category=category,
        split=split,
        subtag=subtag,
    )


def _positive_split(index: int, train_n: int, cal_n: int) -> SplitName:
    if index < train_n:
        return "train"
    if index < train_n + cal_n:
        return "cal"
    return "test"


def _stdlib_records() -> list[tuple[str, str, str]]:
    records: list[tuple[str, str, str]] = []
    seen_text: set[str] = set()
    seen_ids: set[str] = set()
    for module_name in STDLIB_MODULES:
        module = importlib.import_module(module_name)
        for obj in _module_callables(module):
            try:
                source_lines, lineno = inspect.getsourcelines(obj)
            except (OSError, TypeError):
                continue
            source = textwrap.dedent("".join(source_lines))
            line_count = len(source.splitlines())
            if line_count < 5 or line_count > 40:
                continue
            try:
                ast.parse(source)
            except SyntaxError:
                continue
            normalized = normalize_text(source)
            if normalized in seen_text:
                continue
            qualname = getattr(obj, "__qualname__", getattr(obj, "__name__", "fn"))
            if "<" in qualname:
                continue
            sample_id = f"pos_stdlib_python:{module_name}:{qualname}:{lineno}"
            if sample_id in seen_ids:
                continue
            seen_text.add(normalized)
            seen_ids.add(sample_id)
            subtag = module_name.split(".")[0]
            records.append((sample_id, source, subtag))
    return records


def _module_callables(module: object) -> list[object]:
    found: list[object] = []
    module_name = getattr(module, "__name__", "")
    for _name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) and getattr(obj, "__module__", None) == module_name:
            found.append(obj)
        elif inspect.isclass(obj) and getattr(obj, "__module__", None) == module_name:
            for _method_name, method in inspect.getmembers(obj, inspect.isfunction):
                if getattr(method, "__module__", None) == module_name:
                    found.append(method)
    return found


def _load_clauses(domain: str) -> list[tuple[str, str]]:
    path = _DATA_DIR / f"{domain}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    rows: list[tuple[str, str]] = []
    for clause in payload["clauses"]:
        text = str(clause["text"]).strip()
        clause_id = str(clause["id"]).strip()
        if text and clause_id:
            rows.append((clause_id, text))
    rows.sort(key=lambda item: item[0])
    return rows


def _piggyback_samples(
    samples: list[BenchmarkSample],
    clause_tails: list[tuple[str, list[tuple[str, str]]]],
) -> list[BenchmarkSample]:
    donors = [
        sample
        for sample in samples
        if sample.category == "pos_stdlib_python" and sample.split == "test"
    ]
    donors.sort(key=lambda sample: sample.sample_id)
    if len(donors) != 90:
        raise ValueError(f"donantes stdlib de test={len(donors)} != 90")
    clean_payloads = _select_clean_payloads(clause_tails, samples)
    occupied = {
        normalize_text(sample.text) for sample in samples if sample.split in {"train", "cal"}
    }
    foreign = [item for item in FOREIGN_SNIPPETS if item[0] in {"bash", "sql"}]
    if len(foreign) < 30:
        raise ValueError("faltan snippets bash/sql para piggybacking")
    attacks: list[BenchmarkSample] = []
    for index, donor in enumerate(donors):
        if index < 30:
            kind = "docstring"
            text = _inject_docstring(donor.text, clean_payloads[index])
        elif index < 60:
            kind = "prompt_injection"
            text = f"```python\n{donor.text.rstrip()}\n```\n\n{clean_payloads[index]}\n"
        else:
            kind = "foreign_block"
            subtag, _name, snippet = foreign[index - 60]
            text = (
                f"```python\n{donor.text.rstrip()}\n```\n\n"
                f"```{subtag}\n{snippet.rstrip()}\n```\n"
            )
        if normalize_text(text) in occupied:
            text = _disambiguate_occupied_attack(text, kind, index)
        attacks.append(
            _sample(
                f"neg_piggybacking::{kind}::{donor.sample_id}",
                text,
                False,
                "neg_piggybacking",
                "test",
                kind,
            )
        )
    return attacks


def _select_clean_payloads(
    clause_tails: list[tuple[str, list[tuple[str, str]]]],
    samples: list[BenchmarkSample],
) -> list[str]:
    """Seis cláusulas sobrantes por dominio, ausentes del corpus y sin meta-vocabulario."""
    occupied = {normalize_text(sample.text) for sample in samples}
    payloads: list[str] = []
    for domain, clauses in clause_tails:
        chosen: list[str] = []
        for _clause_id, text in clauses:
            stripped = text.strip()
            if len(stripped) < 60:
                continue
            if normalize_text(text) in occupied:
                continue
            if any(bad in stripped.lower() for bad in _BANNED_META_SUBSTRINGS):
                continue
            chosen.append(stripped)
            if len(chosen) == _CLEAN_PAYLOADS_PER_DOMAIN:
                break
        if len(chosen) != _CLEAN_PAYLOADS_PER_DOMAIN:
            raise ValueError(
                f"{domain} no aporta {_CLEAN_PAYLOADS_PER_DOMAIN} clausulas limpias "
                f"para piggybacking (hay {len(chosen)})"
            )
        payloads.extend(chosen)
    if len(payloads) != _CLEAN_PAYLOADS_PER_DOMAIN * (len(SEEN_DOMAINS) + len(OOD_DOMAINS)):
        raise ValueError(f"payloads limpios={len(payloads)} != 60")
    return payloads


def _disambiguate_occupied_attack(text: str, kind: str, index: int) -> str:
    """Separa un ataque que copió un texto de train/cal sin reintroducir vocabulario vedado."""
    marker = f"# aislado {index}\n"
    if kind == "foreign_block":
        updated = text.replace("\n```\n\n```", f"\n{marker}```\n\n```", 1)
        if updated == text:
            raise ValueError(f"no se pudo aislar el foreign_block {index}")
        return updated
    return f"{text.rstrip()}\n{marker}"


def _inject_docstring(source: str, payload: str) -> str:
    tree = ast.parse(textwrap.dedent(source))
    docstring = ast.Expr(value=ast.Constant(payload))
    placed = False
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            node.body.insert(0, docstring)
            placed = True
            break
    if not placed:
        tree.body.insert(0, docstring)
    ast.fix_missing_locations(tree)
    rendered = ast.unparse(tree)
    if payload not in rendered:
        raise ValueError("el docstring inyectado no sobrevivio al unparse")
    return rendered + "\n"


def _assert_contract(samples: list[BenchmarkSample]) -> None:
    by_category = Counter(sample.category for sample in samples)
    expected = {
        "pos_stdlib_python": 300,
        "pos_business_python": 60,
        "neg_seen_domain": 200,
        "neg_unseen_domain_ood": 150,
        "neg_other_language": 60,
        "neg_piggybacking": 90,
    }
    for category, count in expected.items():
        if by_category[category] != count:
            raise ValueError(f"{category}={by_category[category]} != {count}")
    split_counts = {
        "pos_stdlib_python": {"train": 150, "cal": 60, "test": 90},
        "pos_business_python": {"train": 30, "cal": 12, "test": 18},
        "neg_seen_domain": {"train": 120, "cal": 0, "test": 80},
        "neg_unseen_domain_ood": {"train": 0, "cal": 0, "test": 150},
        "neg_other_language": {"train": 0, "cal": 0, "test": 60},
        "neg_piggybacking": {"train": 0, "cal": 0, "test": 90},
    }
    observed: dict[str, Counter[str]] = {category: Counter() for category in expected}
    for sample in samples:
        observed[sample.category][sample.split] += 1
        if sample.category.startswith("pos_") and not sample.is_legitimate_python:
            raise ValueError(f"positivo ilegítimo: {sample.sample_id}")
        if sample.category.startswith("neg_") and sample.is_legitimate_python:
            raise ValueError(f"negativo marcado como python legitimo: {sample.sample_id}")
        if sample.split == "cal" and not sample.is_legitimate_python:
            raise ValueError(f"calibracion con negativo: {sample.sample_id}")
    for category, counts in split_counts.items():
        for split, count in counts.items():
            if observed[category][split] != count:
                raise ValueError(f"{category}/{split}={observed[category][split]} != {count}")
    business_tags = Counter(
        sample.subtag for sample in samples if sample.category == "pos_business_python"
    )
    for subtag in ("finanzas", "medicina", "derecho", "gastronomia", "astronomia"):
        if business_tags[subtag] != 12:
            raise ValueError(f"negocio {subtag}={business_tags[subtag]} != 12")
    seen_tags = Counter(sample.subtag for sample in samples if sample.category == "neg_seen_domain")
    for domain in SEEN_DOMAINS:
        if seen_tags[domain] != 40:
            raise ValueError(f"visto {domain}={seen_tags[domain]} != 40")
    ood_tags = Counter(
        sample.subtag for sample in samples if sample.category == "neg_unseen_domain_ood"
    )
    for domain in OOD_DOMAINS:
        if ood_tags[domain] != 30:
            raise ValueError(f"ood {domain}={ood_tags[domain]} != 30")
