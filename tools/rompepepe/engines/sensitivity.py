"""Sensitivity Analysis and Threshold Boundary Sweep Engine.

Explores the phase transitions of the Dual-Gate Spectral Equalizer by systematically
relaxing the Quorum threshold K, toggling universal structural noise pruning, and
benchmarking against an industry-standard centroid-based Cosine Difference/Similarity classifier.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt

from ddi_fw.corte import VOTE_SOLO_A, VOTE_SOLO_B, evaluar_corte_espectral, votar_vector
from ddi_fw.embedder import BaseEmbedder, get_embedder, load_rows, rows_matrices
from ddi_fw.hoja import RUIDO_UNIVERSAL_BGE_M3, candados_canonicos
from ddi_fw.ingress import Policy
from ddi_fw.splitter import split_clauses
from rompepepe.baselines.cosine_classifier import CosineClassifier, CosineVerdict

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class EvaluationPoint:
    prompt: str
    category: str
    expected: str  # "PASS" (legit) or "BREACH" (adversarial)
    passed: bool
    details: dict[str, Any]


@dataclass
class SweepMetrics:
    total_samples: int
    adversarial_samples: int
    legitimate_samples: int
    true_positives: int  # legit passed
    false_positives: int  # legit blocked
    true_negatives: int  # adv blocked (contained)
    false_negatives: int  # adv passed (bypassed!)
    far: float  # False Acceptance Rate (bypass rate) = FN / (FN + TN)
    frr: float  # False Rejection Rate (over-blocking) = FP / (FP + TP)
    category_bypass_counts: dict[str, int] = field(default_factory=dict)
    flipped_prompts: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class SensitivityRunResult:
    spectral_sweep: dict[str, SweepMetrics]
    cosine_delta_sweep: dict[float, SweepMetrics]
    cosine_forbid_sweep: dict[float, SweepMetrics]
    prompts_telemetry: list[dict[str, Any]]
    config_summary: dict[str, Any]


class SensitivityAnalysisEngine:
    def __init__(
        self,
        rows_path: Path,
        embedder: BaseEmbedder | None = None,
        allowed_alma: str = "python",
        forbidden_almas: list[str] | None = None,
    ):
        self.rows_path = rows_path
        self.embedder = embedder or get_embedder("bge-m3")
        self.allowed_alma = allowed_alma

        if not self.rows_path.is_file():
            raise FileNotFoundError(f"Rows file not found: {self.rows_path}")

        raw_rows = load_rows(self.rows_path)
        self.matrices = rows_matrices(raw_rows)
        all_almas = list(self.matrices.keys())
        self.forbidden_almas = (
            forbidden_almas if forbidden_almas is not None else [a for a in all_almas if a != self.allowed_alma]
        )
        self.policy = Policy(allowed=self.allowed_alma, forbidden=frozenset(self.forbidden_almas))

        # Build locks
        self.locks = candados_canonicos(
            self.matrices,
            ruido_indices=RUIDO_UNIVERSAL_BGE_M3,
            modo_espectral=True,
            quorum_ratio=0.10,
        )
        self.required_locks = [
            lock
            for lock in self.locks.values()
            if self.policy.allowed in {lock.hoja.alma_a, lock.hoja.alma_b}
        ]

        # Initialize Cosine Classifier Baseline
        self.cosine_classifier = CosineClassifier.from_rows_file(
            self.rows_path,
            allowed_alma=self.allowed_alma,
            forbidden_almas=self.forbidden_almas,
        )

        # In-memory caches for fast evaluation
        self._clause_embedding_cache: dict[str, npt.NDArray[np.float32]] = {}
        self._prompt_clauses_cache: dict[str, list[str]] = {}

    def _get_clause_vector(self, clause: str) -> npt.NDArray[np.float32]:
        if clause not in self._clause_embedding_cache:
            if hasattr(self.embedder, "embed_text"):
                vec = self.embedder.embed_text(clause)
            elif hasattr(self.embedder, "embed_batch"):
                vec = self.embedder.embed_batch([clause])[0]
            elif hasattr(self.embedder, "embed"):
                vec = self.embedder.embed([clause])[0]
            else:
                raise TypeError(f"Embedder {self.embedder} does not support embedding.")
            self._clause_embedding_cache[clause] = np.asarray(vec, dtype=np.float32)
        return self._clause_embedding_cache[clause]

    def _get_prompt_clauses(self, prompt: str) -> list[str]:
        if prompt not in self._prompt_clauses_cache:
            clauses = split_clauses(prompt)
            self._prompt_clauses_cache[prompt] = clauses if clauses else [prompt]
        return self._prompt_clauses_cache[prompt]

    def evaluate_spectral_prompt(
        self,
        prompt: str,
        quorum_min: int,
        prune_noise: bool = True,
    ) -> tuple[bool, dict[str, Any]]:
        """Evaluates a prompt using the Dual-Gate Spectral Equalizer with specific K and noise setting.

        Returns: (passed: bool, details: dict)
        """
        clauses = self._get_prompt_clauses(prompt)
        ruido = RUIDO_UNIVERSAL_BGE_M3 if prune_noise else None

        clause_results = []
        for clause in clauses:
            vec = self._get_clause_vector(clause)
            clause_breach = False
            clause_metrics = {}

            for lock in self.required_locks:
                votos = votar_vector(vec, lock.hoja)
                trigo = lock.ejes_trigo if hasattr(lock, "ejes_trigo") else None
                label, met = evaluar_corte_espectral(
                    votos,
                    ejes_trigo=trigo,
                    quorum_min=quorum_min,
                    ruido_indices=ruido,
                )
                clause_metrics[lock.pair_id] = {
                    "label": label,
                    "votos_trigo_a": met["votos_trigo_a"],
                    "votos_trigo_b": met["votos_trigo_b"],
                    "votos_trigo_ambas": met["votos_trigo_ambas"],
                }

                # Fail-closed ingress rule:
                # If lock has allowed as alma_a, label must be "left".
                # If lock has allowed as alma_b, label must be "right".
                expected_label = "left" if lock.hoja.alma_a == self.allowed_alma else "right"
                if label != expected_label:
                    clause_breach = True
                    break

            clause_results.append({
                "clause": clause,
                "passed": not clause_breach,
                "metrics": clause_metrics,
            })
            if clause_breach:
                return False, {"clauses": clause_results, "reason": "clause_breach"}

        return True, {"clauses": clause_results, "reason": "all_clauses_passed"}

    def evaluate_cosine_prompt(
        self,
        prompt: str,
        delta_threshold: float = 0.0,
        max_forbid_threshold: float = 0.80,
    ) -> tuple[bool, CosineVerdict]:
        """Evaluates a prompt using the centroid Cosine difference/similarity baseline."""
        clauses = self._get_prompt_clauses(prompt)
        # In multi-clause ingress, any breach blocks prompt
        worst_verdict: CosineVerdict | None = None
        for clause in clauses:
            vec = self._get_clause_vector(clause)
            verdict = self.cosine_classifier.evaluate_vector(
                vec,
                delta_threshold=delta_threshold,
                max_forbid_threshold=max_forbid_threshold,
            )
            if worst_verdict is None or verdict.delta_cosine < worst_verdict.delta_cosine:
                worst_verdict = verdict

            if not verdict.passed_delta:
                return False, verdict

        return True, worst_verdict if worst_verdict is not None else verdict

    def run_sweep(
        self,
        dataset: list[dict[str, Any]],
        quorum_range: list[int] | None = None,
        cosine_delta_range: list[float] | None = None,
        cosine_forbid_range: list[float] | None = None,
    ) -> SensitivityRunResult:
        """Executes full parameter sweep across dataset."""
        k_values = quorum_range or [103, 75, 50, 35, 30, 25, 20, 15, 10, 5]
        cosine_deltas = cosine_delta_range or [-0.10, -0.05, 0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30]
        cosine_forbids = cosine_forbid_range or [0.60, 0.65, 0.70, 0.75, 0.80, 0.85]

        logger.info(f"Pre-embedding {len(dataset)} prompts...")
        # Pre-cache all clause embeddings
        for item in dataset:
            clauses = self._get_prompt_clauses(item["prompt"])
            for c in clauses:
                self._get_clause_vector(c)
        logger.info(f"Cached {len(self._clause_embedding_cache)} unique clauses.")

        spectral_sweep: dict[str, SweepMetrics] = {}
        prompts_telemetry: list[dict[str, Any]] = []

        # 1. Spectral Sweeps (with noise pruning and without noise pruning)
        for prune in [True, False]:
            prev_passed_set: set[int] = set()
            for k in k_values:
                key = f"K={k}|prune={prune}"
                tp, fp, tn, fn = 0, 0, 0, 0
                cat_bypasses: dict[str, int] = {}
                current_passed_set: set[int] = set()
                flips: list[dict[str, Any]] = []

                for idx, item in enumerate(dataset):
                    prompt = item["prompt"]
                    cat = item["category"]
                    is_legit = (cat == "legitimate_python")

                    passed, details = self.evaluate_spectral_prompt(prompt, quorum_min=k, prune_noise=prune)
                    if passed:
                        current_passed_set.add(idx)

                    if is_legit:
                        if passed:
                            tp += 1
                        else:
                            fp += 1
                    else:
                        if passed:
                            fn += 1  # Bypass!
                            cat_bypasses[cat] = cat_bypasses.get(cat, 0) + 1
                        else:
                            tn += 1  # Contained

                    # Detect flip from blocked to passed as K drops
                    if passed and (idx not in prev_passed_set) and prev_passed_set:
                        flips.append({
                            "prompt_idx": idx,
                            "category": cat,
                            "prompt_snippet": prompt[:80],
                            "k_flipped": k,
                        })

                prev_passed_set = current_passed_set
                far = (fn / (fn + tn)) if (fn + tn) > 0 else 0.0
                frr = (fp / (fp + tp)) if (fp + tp) > 0 else 0.0

                spectral_sweep[key] = SweepMetrics(
                    total_samples=len(dataset),
                    adversarial_samples=tn + fn,
                    legitimate_samples=tp + fp,
                    true_positives=tp,
                    false_positives=fp,
                    true_negatives=tn,
                    false_negatives=fn,
                    far=far,
                    frr=frr,
                    category_bypass_counts=cat_bypasses,
                    flipped_prompts=flips,
                )

        # 2. Cosine Delta Sweep
        cosine_delta_sweep: dict[float, SweepMetrics] = {}
        for delta_th in cosine_deltas:
            tp, fp, tn, fn = 0, 0, 0, 0
            cat_bypasses: dict[str, int] = {}

            for item in dataset:
                prompt = item["prompt"]
                cat = item["category"]
                is_legit = (cat == "legitimate_python")

                passed, _ = self.evaluate_cosine_prompt(prompt, delta_threshold=delta_th)
                if is_legit:
                    if passed:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if passed:
                        fn += 1
                        cat_bypasses[cat] = cat_bypasses.get(cat, 0) + 1
                    else:
                        tn += 1

            far = (fn / (fn + tn)) if (fn + tn) > 0 else 0.0
            frr = (fp / (fp + tp)) if (fp + tp) > 0 else 0.0

            cosine_delta_sweep[delta_th] = SweepMetrics(
                total_samples=len(dataset),
                adversarial_samples=tn + fn,
                legitimate_samples=tp + fp,
                true_positives=tp,
                false_positives=fp,
                true_negatives=tn,
                false_negatives=fn,
                far=far,
                frr=frr,
                category_bypass_counts=cat_bypasses,
            )

        # 3. Cosine Forbid Threshold Sweep (absolute proximity to forbidden)
        cosine_forbid_sweep: dict[float, SweepMetrics] = {}
        for forbid_th in cosine_forbids:
            tp, fp, tn, fn = 0, 0, 0, 0
            cat_bypasses = {}

            for item in dataset:
                prompt = item["prompt"]
                cat = item["category"]
                is_legit = (cat == "legitimate_python")

                # Evaluate passed_forbid
                clauses = self._get_prompt_clauses(prompt)
                prompt_passed = True
                for c in clauses:
                    v = self._get_clause_vector(c)
                    verdict = self.cosine_classifier.evaluate_vector(v, max_forbid_threshold=forbid_th)
                    if not verdict.passed_forbid:
                        prompt_passed = False
                        break

                if is_legit:
                    if prompt_passed:
                        tp += 1
                    else:
                        fp += 1
                else:
                    if prompt_passed:
                        fn += 1
                        cat_bypasses[cat] = cat_bypasses.get(cat, 0) + 1
                    else:
                        tn += 1

            far = (fn / (fn + tn)) if (fn + tn) > 0 else 0.0
            frr = (fp / (fp + tp)) if (fp + tp) > 0 else 0.0

            cosine_forbid_sweep[forbid_th] = SweepMetrics(
                total_samples=len(dataset),
                adversarial_samples=tn + fn,
                legitimate_samples=tp + fp,
                true_positives=tp,
                false_positives=fp,
                true_negatives=tn,
                false_negatives=fn,
                far=far,
                frr=frr,
                category_bypass_counts=cat_bypasses,
            )

        # 4. Detailed Telemetry per Prompt (comparing baseline vs K=25 and Cosine)
        for idx, item in enumerate(dataset):
            prompt = item["prompt"]
            cat = item["category"]
            c_vec = self._get_clause_vector(self._get_prompt_clauses(prompt)[0])
            cos_verdict = self.cosine_classifier.evaluate_vector(c_vec)
            spec_pass_103, _ = self.evaluate_spectral_prompt(prompt, quorum_min=103, prune_noise=True)
            spec_pass_25, _ = self.evaluate_spectral_prompt(prompt, quorum_min=25, prune_noise=True)
            spec_pass_10, _ = self.evaluate_spectral_prompt(prompt, quorum_min=10, prune_noise=True)

            prompts_telemetry.append({
                "prompt_idx": idx,
                "category": cat,
                "prompt_snippet": prompt.replace("\n", " ")[:90],
                "expected": item.get("expected", "BREACH"),
                "spectral_K103": spec_pass_103,
                "spectral_K25": spec_pass_25,
                "spectral_K10": spec_pass_10,
                "cosine_delta": cos_verdict.delta_cosine,
                "cosine_sim_python": cos_verdict.sim_allowed,
                "cosine_max_forbid": cos_verdict.max_sim_forbidden,
                "closest_forbidden": cos_verdict.closest_forbidden_alma,
            })

        return SensitivityRunResult(
            spectral_sweep=spectral_sweep,
            cosine_delta_sweep=cosine_delta_sweep,
            cosine_forbid_sweep=cosine_forbid_sweep,
            prompts_telemetry=prompts_telemetry,
            config_summary={
                "k_values": k_values,
                "cosine_deltas": cosine_deltas,
                "cosine_forbids": cosine_forbids,
                "total_prompts": len(dataset),
                "adversarial_count": len([d for d in dataset if d["category"] != "legitimate_python"]),
                "legitimate_count": len([d for d in dataset if d["category"] == "legitimate_python"]),
            },
        )
