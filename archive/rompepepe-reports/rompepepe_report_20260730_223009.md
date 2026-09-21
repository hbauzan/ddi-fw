# Quality Assurance & Semantic Boundary Report — Pepe ('rompepepe')

**Report Generated:** 2026-07-30 22:30:09
**Session ID:** `adaptive_fuzzing_20260730_222911`
**Exploration Strategy:** `ADAPTIVE_FUZZING`
**Target System Base URL:** `http://localhost:8000`

## Executive Summary

| Metric | Value |
| :--- | :--- |
| Total Tests Executed | `40` |
| Passed Queries (Allowed) | `0` (0.0%) |
| Blocked Queries (Restricted) | `40` (100.0%) |
| Boundary Transition Events | `0` |
| Average REST Latency | `1440.64 ms` |
| Session Status | `COMPLETED` |

> [!WARNING]
> High boundary restriction level detected (100.0% blocked). Review filter thresholds.

## System Behavioral Boundaries & Sensitivity Analysis

### Filter Breach Breakdown

| Breach Reason | Trigger Count | Share % |
| :--- | :--- | :--- |
| `cosine` | `40` | `100.0%` |


## Telemetry Traces & Boundary Transition Events

_No sharp boundary transition points detected in this test run._


## Actionable Developer & AI Tuning Recommendations

1. **Cosine Similarity Calibration:**
   - Cosine threshold appears well-balanced for the tested queries.
2. **Excitation Accumulator Sensitivity:**
   - Keep `excitation_threshold` at `150-170` to prevent multi-part prompt bypasses while avoiding legitimate prompt blocking.
3. **Pipeline Evaluation Ordering:**
   - Optimal recommended pipeline sequence: `Cosine (Order 1) -> Entropy Noise (Order 2) -> Excitation (Order 3)` for minimal latency overhead.