# Dual-Gate Spectral Quorum (Option C) & The Deletor Hypothesis: Deterministic LLM Semantic Containment via Non-Cosine Coordinate Energy

- **Author / Origin**: Héctor Bauzán (`deletor`) & Lead Systems Architecture Agent
- **Target Audience**: Downstream AI Coding Agents, Mechanistic Interpretability Researchers, AppSec & Systems Engineers
- **Status**: Research Specification & Formal Implementation Protocol
- **Date**: 2026-09-19
- **Repository Pin**: `ddi-fw` (Deep Dimensional Inspector Firewall) v0.2.0

---

## 1. Executive Summary & Abstract

In high-assurance Large Language Model (LLM) security, semantic firewalls must prevent adversarial prompt injection, cross-domain data exfiltration, and piggybacking attacks without relying on non-deterministic heuristics or fuzzy similarity scores.

The foundational design of `ddi-fw` relied on **Level 1 (The Single-Axis Guillotine)**: finding a dimension $d \in [0, D-1]$ where the bounding coordinate intervals of two domains do not overlap ($gap > 0$). However, empirical inspection across 5 extended corpora ($N=110$ clauses each, $>2000$ words per deck) demonstrated that as corpus natural language richness scales, the probability of finding a single isolated disjoint dimension in unpruned raw decks drops to **zero** (`disjoint_count = 0` across all 10 canonical pairs in both `BAAI/bge-m3` and `Alibaba-NLP/gte-Qwen2-1.5B-instruct`).

The **Deletor Hypothesis** (formulated by Héctor) solves this limitation by shifting the inspection paradigm from a single scalar knife-edge to a **multidimensional spectral equalizer**:
> *Dense embeddings do not encode domain separation in a single isolated dimension, but as a coordinated harmonic chord across an entire subspace of dimensions. A semantic firewall must inspect the collective mass of resonance—evaluating positive native excitation and negative foreign containment simultaneously.*

This document formalizes **Option C (Dual-Gate Spectral Quorum)** as the mathematically rigorous, deterministically provable implementation of the Deletor Hypothesis.

---

## 2. Fundamental Axioms: The Fatal Flaw of Cosine Similarity (Level 0)

Before formalizing the Spectral Quorum, we must establish the core architectural axiom of `ddi-fw` regarding cosine similarity:

```
[Prompt: 200 words of benign cooking recipe + 10 words of malicious SQL injection]
                               │
       ┌───────────────────────┴───────────────────────┐
       ▼                                               ▼
COSINE SIMILARITY (FLAWED)                   DDI COORDINATE INSPECTION (DETERMINISTIC)
Dot product / Centroid angle                 Clause-level interval inclusion [lo, hi]
       │                                               │
Angle shifts by < 0.03                       Malicious clause isolated at Ingress:
(Diluted into benign average)                Excites exclusive SQL/Code dimensions:
       │                                               │
VERDICT: BYPASS (FALSE NEGATIVE)             VERDICT: 403 BREACH (ZERO DILUTION)
```

### Invariant C-AXIOM-01 (Membership is Not Cosine)
1. **No Cosine in `decide()`**: Cosine similarity averages the entire embedding vector, enabling **piggybacking attacks** where short hostile clauses hide inside large benign prompts.
2. **No Centroids or Row Means**: Centroids collapse token variance and erase edge anomalies.
3. **No Float Rounding**: All calculations must operate on native IEEE 754 float32 coordinate values without truncation or `.6f` approximations.
4. **Deterministic Boolean Interval Inclusion**: An input vector $v \in \mathbb{R}^D$ is inspected by checking coordinate membership $v_d \in [lo_d, hi_d]$ for each dimension $d \in \{0, \dots, D-1\}$.

---

## 3. Empirical Evidence: Extended 5-Almas × 2-Engine Inspection Ledger

During the `v0.2.0` inspection cycle, 5 canonical corpora were measured across two transformer architectures without heuristic pruning (`--no-prune`):
- **Corpora**: `python`, `legal`, `receta`, `medicina`, `astronomia` (110 clauses each, $N=110$, pairwise Jaccard index $< 0.05$).
- **Engines**: `BAAI/bge-m3` (1024-D FP32) and `Alibaba-NLP/gte-Qwen2-1.5B-instruct` (1536-D FP16).

### 3.1. Single-Axis Guillotine Collapse (Level 1)
Across all 10 canonical pairs, the raw disjoint axis count was identically **0**:

| Pair | BGE-M3 (1024-D) Disjoint Count | Qwen2 1.5B (1536-D) Disjoint Count | Level 1 Status |
| :--- | :---: | :---: | :---: |
| `python_receta` | 0 | 0 | `unpublished` (fail-closed) |
| `python_legal` | 0 | 0 | `unpublished` (fail-closed) |
| `legal_receta` | 0 | 0 | `unpublished` (fail-closed) |
| `python_medicina` | 0 | 0 | `unpublished` (fail-closed) |
| `python_astronomia` | 0 | 0 | `unpublished` (fail-closed) |
| `legal_medicina` | 0 | 0 | `unpublished` (fail-closed) |
| `legal_astronomia` | 0 | 0 | `unpublished` (fail-closed) |
| `receta_medicina` | 0 | 0 | `unpublished` (fail-closed) |
| `receta_astronomia` | 0 | 0 | `unpublished` (fail-closed) |
| `medicina_astronomia` | 0 | 0 | `unpublished` (fail-closed) |

### 3.2. Empirical Validation of the Spectral Equalizer (The Deletor Phenomenon)
While zero dimensions had $gap > 0$ across the entire deck, computing the coordinate voting census across all clauses revealed **absolute domain segregation in exclusive coordinate subspaces**.

In every clause evaluation, each dimension $d$ falls into one of four mutually exclusive states:
- `solo_a`: Coordinate falls exclusively within the observed bounds of domain $A$ ($v_d \in A \land v_d \notin B$).
- `solo_b`: Coordinate falls exclusively within the observed bounds of domain $B$ ($v_d \notin A \land v_d \in B$).
- `ambas`: Coordinate falls within the overlapping bounds of both domains ($v_d \in A \land v_d \in B$).
- `ninguna`: Coordinate falls outside both domains ($v_d \notin A \land v_d \notin B$).

#### Measured Census in `BAAI/bge-m3` (1024-D)
Source: [`ddi_fw/out/extended_bge/press.json`](file:///Users/hbauzan/treepwood/DDI%20Firewall%20-%20Deep%20Dimensional%20Inspector/ddi-fw/ddi_fw/out/extended_bge/press.json)

| Canonical Pair | Evaluated Deck | `solo_a` Extrema $[lo, hi]$ | `solo_b` Extrema $[lo, hi]$ | `ambas` Extrema $[lo, hi]$ |
| :--- | :--- | :---: | :---: | :---: |
| **`python_receta`** | `python` (110 clauses) | **$[47, 92]$** | **$[0, 0]$ (Zero Foreign)** | $[932, 977]$ |
| | `receta` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[37, 77]$** | $[947, 987]$ |
| **`python_legal`** | `python` (110 clauses) | **$[28, 75]$** | **$[0, 0]$ (Zero Foreign)** | $[949, 996]$ |
| | `legal` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[33, 73]$** | $[951, 991]$ |
| **`legal_receta`** | `legal` (110 clauses) | **$[53, 95]$** | **$[0, 0]$ (Zero Foreign)** | $[929, 971]$ |
| | `receta` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[44, 93]$** | $[931, 980]$ |
| **`python_medicina`** | `python` (110 clauses) | **$[34, 73]$** | **$[0, 0]$ (Zero Foreign)** | $[951, 990]$ |
| | `medicina` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[33, 70]$** | $[954, 991]$ |
| **`python_astronomia`**| `python` (110 clauses) | **$[30, 72]$** | **$[0, 0]$ (Zero Foreign)** | $[952, 994]$ |
| | `astronomia` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[29, 68]$** | $[956, 995]$ |
| **`legal_medicina`** | `legal` (110 clauses) | **$[37, 88]$** | **$[0, 0]$ (Zero Foreign)** | $[936, 987]$ |
| | `medicina` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[43, 86]$** | $[938, 981]$ |
| **`legal_astronomia`** | `legal` (110 clauses) | **$[31, 88]$** | **$[0, 0]$ (Zero Foreign)** | $[936, 993]$ |
| | `astronomia` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[56, 99]$** | $[925, 968]$ |
| **`receta_medicina`** | `receta` (110 clauses) | **$[33, 73]$** | **$[0, 0]$ (Zero Foreign)** | $[951, 991]$ |
| | `medicina` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[37, 91]$** | $[933, 987]$ |
| **`receta_astronomia`**| `receta` (110 clauses) | **$[35, 70]$** | **$[0, 0]$ (Zero Foreign)** | $[954, 989]$ |
| | `astronomia` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[51, 99]$** | $[925, 973]$ |
| **`medicina_astronomia`**| `medicina` (110 clauses)| **$[24, 58]$** | **$[0, 0]$ (Zero Foreign)** | $[966, 1000]$ |
| | `astronomia` (110 clauses) | **$[0, 0]$ (Zero Foreign)** | **$[30, 81]$** | $[943, 994]$ |

> [!IMPORTANT]
> **The Empirical Law of Spectral Purity**:
> In 100% of tested clauses across all 10 pairs ($550 \text{ clauses} \times 2 \text{ evaluations}$):
> 1. Legitimate clauses of domain $A$ exhibited **$\mathbf{solo\_b == 0}$ unconditionally** ($lo=0, hi=0$).
> 2. Legitimate clauses of domain $B$ exhibited **$\mathbf{solo\_a == 0}$ unconditionally** ($lo=0, hi=0$).
> 3. Active resonance in native exclusive dimensions never dropped below 24 (minimum recorded: 24, maximum: 99).

---

## 4. Mathematical Formulation of Option C (Dual-Gate Quorum)

Let $A$ be the authorized native domain and $B$ be the forbidden target domain.
Let the baseline bounding boxes be defined as:
$$I_A(d) = [lo_A(d), hi_A(d)], \quad I_B(d) = [lo_B(d), hi_B(d)] \quad \forall d \in \{0, \dots, D-1\}$$

For any input clause vector $v \in \mathbb{R}^D$, we define the dimensional membership indicator functions:
$$\chi_A(v, d) = \begin{cases} 1 & \text{if } v_d \in I_A(d) \\ 0 & \text{otherwise} \end{cases}, \quad \chi_B(v, d) = \begin{cases} 1 & \text{if } v_d \in I_B(d) \\ 0 & \text{otherwise} \end{cases}$$

The coordinate energy counts are:
$$solo\_a(v) = \sum_{d=0}^{D-1} \chi_A(v, d) \cdot (1 - \chi_B(v, d))$$
$$solo\_b(v) = \sum_{d=0}^{D-1} (1 - \chi_A(v, d)) \cdot \chi_B(v, d)$$

### 4.1. The Dual-Gate Decision Predicate
The firewall evaluates clause vector $v$ under the **Dual-Gate Predicate** $\mathcal{P}(v)$:

$$\mathcal{P}(v) = \underbrace{(solo\_b(v) == 0)}_{\text{Gate 1: Negative Foreign Exclusion}} \;\land\; \underbrace{(solo\_a(v) \ge \tau_{\text{floor}}(A))}_{\text{Gate 2: Positive Native Resonance}}$$

$$\text{Verdict}(v) = \begin{cases} \text{PASS} & \text{if } \mathcal{P}(v) \text{ is TRUE} \\ \text{BREACH (HTTP 403)} & \text{if } \mathcal{P}(v) \text{ is FALSE} \end{cases}$$

### 4.2. Deterministic Derivation of $\tau_{\text{floor}}(A)$
The native resonance floor $\tau_{\text{floor}}(A)$ is not an arbitrary user guess. It is derived directly from the empirical baseline census stored in `press.json`:

$$\tau_{\text{floor}}(A) = \lfloor \alpha \cdot \min_{c \in \text{Deck}(A)} solo\_a(c) \rfloor$$

Where:
- $\min_{c \in \text{Deck}(A)} solo\_a(c)$ is the frozen historical lower bound (`lo`) recorded in `press.json`.
- $\alpha \in (0, 1]$ is the safety factor. The architectural default is $\mathbf{\alpha = 0.50}$ (providing a 50% safety cushion below the minimum observed native excitation).

#### Concrete Instantiations for `BAAI/bge-m3` ($\alpha = 0.50$):
- **`python` vs `receta`**: $\min(solo\_a) = 47 \implies \mathbf{\tau_{\text{floor}} = 23}$.
- **`python` vs `legal`**: $\min(solo\_a) = 28 \implies \mathbf{\tau_{\text{floor}} = 14}$.
- **`legal` vs `receta`**: $\min(solo\_a) = 53 \implies \mathbf{\tau_{\text{floor}} = 26}$.
- **`medicina` vs `astronomia`**: $\min(solo\_a) = 24 \implies \mathbf{\tau_{\text{floor}} = 12}$.

---

## 5. Architectural Comparison: Why Option C Superior to Options A & B

| Criterion | Option A (Zero-Foreign Footprint) | Option B (Relative Asymmetry Ratio) | Option C (Dual-Gate Quorum) |
| :--- | :--- | :--- | :--- |
| **Mathematical Rule** | $solo\_b == 0$ | $\frac{solo\_a}{solo\_a + solo\_b} \ge \theta$ | $(solo\_b == 0) \land (solo\_a \ge \tau_{\text{floor}})$ |
| **Adversarial Domain Containment** | Absolute ($solo\_b > 0 \implies \text{Cut}$) | Good (drops if $solo\_b$ rises) | **Absolute ($solo\_b > 0 \implies \text{Cut}$)** |
| **Out-of-Distribution (OOD) / Alien Payload Attack** | **VULNERABLE**: Random noise or unmodeled languages have $solo\_b = 0 \land solo\_a = 0$ and would pass. | **UNDEFINED**: If $solo\_a = solo\_b = 0$, division by zero occurs ($\frac{0}{0}$). | **PROTECTED**: $solo\_a < \tau_{\text{floor}}$ immediately triggers BREACH for unmodeled text. |
| **Parameter Stability** | 0 parameters | Requires tuning continuous threshold $\theta \in (0, 1)$ | Derived deterministically from frozen baseline censes ($\alpha = 0.5$). |
| **Alignment with Deletor Hypothesis** | Partial (only checks absence of forbidden domain). | Partial (treats excitation as a ratio, not a mass). | **Complete (demands active mass in native band + zero resonance in forbidden band).** |

---

## 6. Multi-Layer Defense Pipeline Architecture

```
                                  [ Incoming Prompt ]
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 0: Ingress Atomic Clause Segmentation (Sentence & Proposition Splitting)         │
│          - Prevents piggybacking attacks by isolating clauses before embedding.       │
│          - Output: C = [clause_0, clause_1, ..., clause_k]                            │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                        For each clause c_i in C: Embed -> v_i
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 1: Fast-Path Binary Guillotine (Disjoint Coordinate Cut)                        │
│          - Checked if disjoint_count > 0 for lock pair (O(1) execution).              │
│          - If v_i falls into forbidden disjoint interval:                             │
│            ──► IMMEDIATE 403 BREACH (Terminate pipeline)                              │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │ (If disjoint_count == 0 OR Layer 1 passes)
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 2: Dual-Gate Spectral Quorum (Full Subspace Resonator)                          │
│          - Counts solo_a, solo_b, ambas across all D dimensions.                      │
│          - Gate 1: If solo_b > 0 ──► 403 BREACH (Foreign domain pollution)            │
│          - Gate 2: If solo_a < tau_floor ──► 403 BREACH (Insufficient native energy)  │
│          - If both gates pass: Clause c_i is VALIDATED.                               │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                        All clauses in prompt pass Layers 1 & 2
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ UPSTREAM FORWARDING: Query dispatched to target LLM backend                           │
└──────────────────────────────────────────┬────────────────────────────────────────────┘
                                           │
                                  [ LLM Output Stream ]
                                           │
                                           ▼
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ EGRESS HOLD: Zero Speculative Streaming Buffer                                        │
│              - Buffer full response. Segment into clauses. Apply Layer 2 validation.  │
│              - If clean ──► Release tokens to client.                                 │
│              - If infected ──► Withhold stream, emit 403 BREACH.                      │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 7. Deterministic Implementation Instructions for Downstream AI Agents

When implementing the Dual-Gate Spectral Quorum in `ddi-fw`, downstream agents **MUST** follow these exact requirements:

1. **Do Not Touch Core Axioms**:
   - Never import `scipy.spatial.distance.cosine` or introduce cosine into `decide()`.
   - Never use `round()` or truncate float numbers in stored tensors or metadata.
2. **Data Structure Extensions in `corte.py`**:
   - `corte_spectral_quorum(vector, bounds_a, bounds_b, tau_floor) -> Tuple[bool, str, Dict[str, int]]`:
     Compute exact integer counts for `solo_a`, `solo_b`, `ambas`, `ninguna`.
     If `solo_b > 0`, return `(False, "BREACH_FOREIGN_CONTAMINATION", vote_counts)`.
     If `solo_a < tau_floor`, return `(False, "BREACH_INSUFFICIENT_RESONANCE", vote_counts)`.
     Else return `(True, "PASS_SPECTRAL_QUORUM", vote_counts)`.
3. **Census Enrichment in `press.py`**:
   - For each evaluated pair in `press.json`, store `tau_floor_a` and `tau_floor_b` computed via $\lfloor \alpha \cdot \min(solo) \rfloor$.
4. **Integration in `ingress.py`**:
   - In `evaluate_clause()`, if `candado.disjoint_count == 0`, fallback to `corte_spectral_quorum` instead of emitting `unpublished / fail-closed`. This enables full deployment on unpruned corpora.
5. **Testing & TDD**:
   - Write unit tests in `tests/test_ddi_spectral_quorum.py` verifying:
     - Synthetic vector with $solo\_b > 0 \implies \text{BREACH}$.
     - Synthetic vector with $solo\_b == 0 \land solo\_a < \tau_{\text{floor}} \implies \text{BREACH}$.
     - Legitimate vector from native dataset $\implies \text{PASS}$.
     - 100% test pass rate with `uv run pytest`.

---

## 8. Summary Conclusion

The Deletor Hypothesis replaces the fragility of single-axis knife-edges with the statistical and deterministic robustness of multidimensional subspace resonance. **Option C (Dual-Gate Spectral Quorum)** provides the formal, zero-cosine, zero-rounding framework necessary to operate production LLM firewalls at arbitrary corpus scales.
