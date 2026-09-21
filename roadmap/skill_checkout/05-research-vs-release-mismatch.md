# 05 — Research vs release mismatch

This is the load-bearing diagnosis. If a successor agent remembers only one file after the verdict, it is this one.

---

## 5.1 Two kinds of work in this repository

### Release work (product)

Examples: change `hold()` to stay fail-closed; reject `stream=true`; 403 without echo; splitter decimal-safe; proxy `/healthz`; a failing unit test on `evaluar_corte_duro`.

Success looks like: pytest green, contract in `architecture_spec.md` still true, no cosine in `decide()`.

Process that fits: TDD, vertical slice, debug loop with a curl/pytest signal, approval gate.

### Research work (geometry lab)

Examples: load `Alibaba-NLP/gte-Qwen2-1.5B-instruct`; `--no-prune` measure; observe `ok_unpublished` on `python_receta`; write `current-research/engines/gte-qwen2-1.5b.md`; Jaccard of two mazos; “does axis 891 still disjoint on this deck?”; sequential embedder A/B.

Success looks like: a **true measurement**, including the measurement “zero disjoint axes”. Unpublished is a finding. Pruning the shared deck to force a green lock is a **product** change and is forbidden on the Qwen2 path.

Process that fits: read adapters + lessons + ledger, run one `uv` command, record native-precision numbers, do not “fix” geometry with epsilon.

---

## 5.2 Where the protocol assumes release work

`SKILL.md` §0 step 4: implement via TDD; bugs via six-phase debug.

`code-design.md`: do not anticipate future tests; minimal code to pass.

`debugging.md`: no theory and no code reading until a red-capable command exists.

`qa-review.md` Spec axis: unrequested behavior is scope creep.

`estilo-comunicacion.md`: if it is closed, do not reopen it.

Those sentences are rational for a proxy ticket. They are **wrong** as the default for `roadmap/archive/ola-q/00-qwen2-live.md`.

Ola Q already had to **fight** the generic protocol:

- `calibrate()` prunes → forbidden for Qwen2
- zero disjoint → `ok_unpublished`, do not prune shared mazos
- numbers only in `current-research/`
- BGE ledger row sealed

That fight is evidence. The skill did not encode the lab. The briefing had to override the skill.

---

## 5.3 Typical lab failures under a literalist protocol

| Human intent | Literalist agent behavior | Correct behavior |
| :--- | :--- | :--- |
| Measure Qwen2 full deck | Call `calibrate()` because TDD “publication” tests want a lock | `measure_and_save` / `--no-prune --out ddi_fw/out/qwen2` |
| Headlines unpublished | Prune mazos or invent gap epsilon to get green | Record `ok_unpublished`; do not touch shared `ddi_fw/data/` |
| “Why zero disjoint?” | Refuse to read `decide.py` until a pytest is red | Read hoja code, decks, adapter, lessons **first** |
| Compare cosine piggyback vs intervals | Refuse any cosine symbol | Cosine may be a **labeled diagnostic**; never `decide()` input |
| Add alma `medicina` | Refuse because Jaccard might break | Measure Jaccard; curate; surgical vetos |
| Live encode | Skip because “tests must not call models” | Default tests stay fake; live is explicit `--run-live` / marker |
| Two models | Load both and OOM | Sequential load-measure-release |
| Plot gaps | Refuse any display rounding | Full-precision source + optional display-only caption |

---

## 5.4 Mode detection (deterministic)

The successor agent MUST classify the user task before applying TDD/debug.

**Research mode IF any of these is true:**

- path or words: `current-research`, `ledger`, `measure_and_save`, `--no-prune`, `disjoint`, `unpublished`, `Jaccard`, `mazo`, `alma` curation, `embedder` live, `press` census of an existing `rows.npz` without changing `decide()`, Q-wave briefing, “why did model Y not publish”
- ticket lives under `roadmap/` and says measurement / live model / do not prune
- the deliverable is markdown numbers, not a change to `decide`/`hold`/proxy contracts

**Release mode IF any of these is true:**

- change to `ddi_fw/` verdict, hold, proxy, splitter, publication rule
- failing product test
- ticket that specifies a **closed** HTTP or function contract to implement
- security posture of the shipping proxy (403 echo, stream 400)

**If both match:** research for the measurement part, release for any product-code part. Do not use research mode as a license to edit `hold()`.

**If neither matches:** ask one question: “release mode (TDD, product contract) or research mode (measure, do not change `decide`/`hold`)?”

Do not ask that question when the ticket already says the mode.

---

## 5.5 What stays identical in both modes

Copy this list into `SKILL.md` as “always”:

- `uv` toolchain (C-AXIOM-11, C-PROC-13)
- secrets (C-AXIOM-11)
- no cosine / mean / top-k / epsilon **in `decide()` and publication** (C-AXIOM-01, C-AXIOM-02)
- native precision in scientific exports (C-AXIOM-07)
- fail-closed on the **product** proxy (C-AXIOM-04, C-AXIOM-05, C-AXIOM-06)
- `BaseEmbedder` seam; default tests fake (C-AXIOM-08)
- do not merge Deletor by accident (C-AXIOM-14)
- do not push/merge without explicit human go-ahead (C-PROC-10)
- do not dump tables into `lessons-learned.md` (C-PROC-07)

---

## 5.6 What changes by mode

| Action | Release | Research |
| :--- | :--- | :--- |
| Read code before a failing command | After a red loop exists, except as debug protocol allows | **Allowed immediately** |
| TDD red-green | **Required** for product behavior | **Not required** for ledger/measure |
| `calibrate()` | Allowed when the ticket wants published locks on the BGE path | **Forbidden** on Qwen2 measure path |
| Change mazos in `ddi_fw/data/` | Only with tests + awareness of `almas` rewrite gotcha | **Forbidden** as a way to green an unpublished measure |
| Spec-axis “scope creep” | Extra product behavior is creep | Extra **recorded diagnostics** are not creep if labeled |
| Reopen a previous number | Do not silently change contracts | **Must** record a new measurement even if it contradicts a headline |
| Murray sandwich | Optional | Optional |
