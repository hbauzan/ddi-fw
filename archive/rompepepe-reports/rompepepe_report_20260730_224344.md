# Quality Assurance & Semantic Boundary Report — Pepe ('rompepepe')

**Report Generated:** 2026-07-30 22:43:44
**Session ID:** `adaptive_fuzzing_20260730_224226`
**Exploration Strategy:** `ADAPTIVE_FUZZING`
**Target System Base URL:** `http://localhost:8000`

## Executive Summary

| Metric | Value |
| :--- | :--- |
| Total Tests Executed | `31` |
| Passed Queries (Allowed) | `0` (0.0%) |
| Blocked Queries (Restricted) | `31` (100.0%) |
| Boundary Transition Events | `0` |
| Average REST Latency | `2108.93 ms` |
| Session Status | `PAUSED` |

> [!WARNING]
> **Execution Paused Due to Token Quota Exhaustion:** Token quota / rate limit exhausted for explorer provider 'google' (Model: 'gemini-3.1-flash-lite') after 3 retries.
> The session state has been cleanly saved at step **31/50**.
> You can resume execution anytime by running `./run_rompepepe.sh` option 7 or `python -m rompepepe.main --resume adaptive_fuzzing_20260730_224226`.


## System Behavioral Boundaries & Sensitivity Analysis

### Filter Breach Breakdown

| Breach Reason | Trigger Count | Share % |
| :--- | :--- | :--- |
| `cosine` | `31` | `100.0%` |


## Telemetry Traces & Boundary Transition Events

_No sharp boundary transition points detected in this test run._


## Actionable Developer & AI Tuning Recommendations

1. **Cosine Similarity Calibration:**
   - Cosine threshold appears well-balanced for the tested queries.
2. **Excitation Accumulator Sensitivity:**
   - Keep `excitation_threshold` at `150-170` to prevent multi-part prompt bypasses while avoiding legitimate prompt blocking.
3. **Pipeline Evaluation Ordering:**
   - Optimal recommended pipeline sequence: `Cosine (Order 1) -> Entropy Noise (Order 2) -> Excitation (Order 3)` for minimal latency overhead.