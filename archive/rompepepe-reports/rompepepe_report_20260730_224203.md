# Quality Assurance & Semantic Boundary Report — Pepe ('rompepepe')

**Report Generated:** 2026-07-30 22:42:03
**Session ID:** `grid_search_20260730_224135`
**Exploration Strategy:** `GRID_SEARCH`
**Target System Base URL:** `http://localhost:8000`

## Executive Summary

| Metric | Value |
| :--- | :--- |
| Total Tests Executed | `612` |
| Passed Queries (Allowed) | `76` (12.4%) |
| Blocked Queries (Restricted) | `536` (87.6%) |
| Boundary Transition Events | `0` |
| Average REST Latency | `44.50 ms` |
| Session Status | `COMPLETED` |

> [!WARNING]
> High boundary restriction level detected (87.6% blocked). Review filter thresholds.

## System Behavioral Boundaries & Sensitivity Analysis

### Filter Breach Breakdown

| Breach Reason | Trigger Count | Share % |
| :--- | :--- | :--- |
| `cosine` | `414` | `77.2%` |
| `excitation` | `122` | `22.8%` |

### Configuration Grid Permutation Metrics

| Cell # | Cosine Thresh | Excitation Thresh | Noise Limit | Mode | Pass Rate | Avg Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `1` | `0.45` | `150` | `3.0` | `positive` | `21.2%` | `46.7ms` |
| `2` | `0.65` | `150` | `3.0` | `positive` | `3.6%` | `42.3ms` |


## Telemetry Traces & Boundary Transition Events

_No sharp boundary transition points detected in this test run._


## Actionable Developer & AI Tuning Recommendations

1. **Cosine Similarity Calibration:**
   - Cosine threshold appears well-balanced for the tested queries.
2. **Excitation Accumulator Sensitivity:**
   - Keep `excitation_threshold` at `150-170` to prevent multi-part prompt bypasses while avoiding legitimate prompt blocking.
3. **Pipeline Evaluation Ordering:**
   - Optimal recommended pipeline sequence: `Cosine (Order 1) -> Entropy Noise (Order 2) -> Excitation (Order 3)` for minimal latency overhead.