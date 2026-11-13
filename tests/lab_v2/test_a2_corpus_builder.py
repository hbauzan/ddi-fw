"""Slice 2: el corpus real es offline, contado y sin fuga entre splits."""

from __future__ import annotations

import ast
import re
from collections import Counter

from ddi_fw.lab_v2.corpus_builder import (
    _BANNED_META_SUBSTRINGS,
    SEEN_DOMAINS,
    BenchmarkSample,
    assert_no_leakage,
    build_test_a_dataset,
    normalize_text,
)

_FENCE_RE = re.compile(r"```([a-zA-Z0-9_+-]*)\n(.*?)```", re.DOTALL)


def _by(samples: list[BenchmarkSample], category: str) -> list[BenchmarkSample]:
    return [sample for sample in samples if sample.category == category]


def test_dataset_counts_splits_and_no_leakage() -> None:
    samples = build_test_a_dataset(seed=42)
    assert len(samples) == 860
    assert_no_leakage(samples)
    counts = Counter((sample.category, sample.split) for sample in samples)
    assert counts[("pos_stdlib_python", "train")] == 150
    assert counts[("pos_stdlib_python", "cal")] == 60
    assert counts[("pos_stdlib_python", "test")] == 90
    assert counts[("pos_business_python", "train")] == 30
    assert counts[("pos_business_python", "cal")] == 12
    assert counts[("pos_business_python", "test")] == 18
    assert counts[("neg_seen_domain", "train")] == 120
    assert counts[("neg_seen_domain", "cal")] == 0
    assert counts[("neg_seen_domain", "test")] == 80
    assert counts[("neg_unseen_domain_ood", "test")] == 150
    assert counts[("neg_unseen_domain_ood", "train")] == 0
    assert counts[("neg_unseen_domain_ood", "cal")] == 0
    assert counts[("neg_other_language", "test")] == 60
    assert counts[("neg_piggybacking", "test")] == 90
    assert all(sample.is_legitimate_python for sample in samples if sample.split == "cal")
    assert all(sample.split == "test" for sample in _by(samples, "neg_other_language"))
    assert all(sample.split == "test" for sample in _by(samples, "neg_piggybacking"))
    seen = Counter(sample.subtag for sample in _by(samples, "neg_seen_domain"))
    assert all(seen[domain] == 40 for domain in SEEN_DOMAINS)


def test_business_code_parses_and_other_languages_do_not() -> None:
    samples = build_test_a_dataset(seed=42)
    business = _by(samples, "pos_business_python")
    assert len(business) == 60
    for sample in business:
        tree = ast.parse(sample.text)
        assert isinstance(tree.body[0], ast.FunctionDef)
    foreign = _by(samples, "neg_other_language")
    languages = Counter(sample.subtag for sample in foreign)
    assert languages["javascript"] == 15
    assert languages["sql"] == 15
    assert languages["bash"] == 15
    assert languages["rust"] + languages["c"] + languages["go"] == 15
    for sample in foreign:
        try:
            ast.parse(sample.text)
        except SyntaxError:
            continue
        raise AssertionError(f"{sample.sample_id} parsea como Python")


def test_piggyback_uses_only_test_stdlib_and_is_reproducible() -> None:
    first = build_test_a_dataset(seed=42)
    second = build_test_a_dataset(seed=42)
    assert [(item.sample_id, item.split, item.text) for item in first] == [
        (item.sample_id, item.split, item.text) for item in second
    ]
    other_seed = build_test_a_dataset(seed=43)
    first_ids = [item.sample_id for item in first if item.category == "pos_stdlib_python"]
    other_ids = [item.sample_id for item in other_seed if item.category == "pos_stdlib_python"]
    assert first_ids != other_ids

    test_ids = {
        item.sample_id
        for item in first
        if item.category == "pos_stdlib_python" and item.split == "test"
    }
    blocked = {
        item.sample_id
        for item in first
        if item.category == "pos_stdlib_python" and item.split in {"train", "cal"}
    }
    kinds = Counter()
    for sample in _by(first, "neg_piggybacking"):
        prefix, kind, donor = sample.sample_id.split("::", 2)
        assert prefix == "neg_piggybacking"
        assert donor in test_ids
        assert donor not in blocked
        kinds[kind] += 1
        assert sample.split == "test"
        assert sample.is_legitimate_python is False
    assert kinds["docstring"] == 30
    assert kinds["prompt_injection"] == 30
    assert kinds["foreign_block"] == 30
    docstring_attacks = [
        sample for sample in _by(first, "neg_piggybacking") if sample.subtag == "docstring"
    ]
    assert all(ast.parse(sample.text) for sample in docstring_attacks)
    train_norms = {
        normalize_text(sample.text) for sample in first if sample.split in {"train", "cal"}
    }
    attack_norms = {normalize_text(sample.text) for sample in _by(first, "neg_piggybacking")}
    assert train_norms.isdisjoint(attack_norms)


def _first_docstring(source: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found = ast.get_docstring(node)
            if found:
                return found
    found = ast.get_docstring(tree)
    if not found:
        raise AssertionError("el ataque docstring no tiene docstring")
    return found


def _has_banned_meta(text: str) -> bool:
    lowered = text.lower()
    return any(bad in lowered for bad in _BANNED_META_SUBSTRINGS)


def test_piggyback_payloads_are_clean_trilingual_clauses() -> None:
    samples = build_test_a_dataset(seed=42)
    assert_no_leakage(samples)
    attacks = [sample for sample in samples if sample.category == "neg_piggybacking"]
    docstrings = [sample for sample in attacks if sample.subtag == "docstring"]
    prompts = [sample for sample in attacks if sample.subtag == "prompt_injection"]
    foreign = [sample for sample in attacks if sample.subtag == "foreign_block"]
    assert len(docstrings) == 30
    assert len(prompts) == 30
    assert len(foreign) == 30
    for sample in docstrings:
        payload = _first_docstring(sample.text)
        assert len(payload) >= 60
        assert not _has_banned_meta(payload)
    for sample in prompts:
        fences = list(_FENCE_RE.finditer(sample.text))
        assert len(fences) == 1
        payload = sample.text[fences[0].end() :].strip()
        assert len(payload) >= 60
        assert not _has_banned_meta(payload)
    for sample in foreign:
        fences = list(_FENCE_RE.finditer(sample.text))
        assert len(fences) == 2
        assert fences[0].group(1) == "python"
        assert fences[1].group(1) in {"bash", "sql"}
        outside = _FENCE_RE.sub("", sample.text)
        assert not outside.strip()
        assert not _has_banned_meta(outside)


def test_assert_no_leakage_rejects_overlapping_text() -> None:
    shared = "texto compartido entre splits que no puede pasar"
    samples = [
        BenchmarkSample("a", shared, True, "pos_business_python", "train", "finanzas"),
        BenchmarkSample("b", shared, True, "pos_business_python", "cal", "finanzas"),
    ]
    try:
        assert_no_leakage(samples)
    except ValueError as exc:
        assert "texto normalizado" in str(exc)
    else:
        raise AssertionError("la fuga de texto no fue rechazada")
