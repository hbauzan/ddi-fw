# Quality Assurance & Semantic Boundary Report — Pepe ('rompepepe')

**Report Generated:** 2026-07-30 22:12:32
**Session ID:** `grid_search_20260730_221018`
**Exploration Strategy:** `GRID_SEARCH`
**Target System Base URL:** `http://localhost:8000`

## Executive Summary

| Metric | Value |
| :--- | :--- |
| Total Tests Executed | `2160` |
| Passed Queries (Allowed) | `792` (36.7%) |
| Blocked Queries (Restricted) | `1368` (63.3%) |
| Boundary Transition Events | `0` |
| Average REST Latency | `57.57 ms` |
| Session Status | `COMPLETED` |

> [!WARNING]
> High boundary restriction level detected (63.3% blocked). Review filter thresholds.

## System Behavioral Boundaries & Sensitivity Analysis

### Filter Breach Breakdown

| Breach Reason | Trigger Count | Share % |
| :--- | :--- | :--- |
| `cosine` | `568` | `41.5%` |
| `excitation` | `400` | `29.2%` |
| `negative:cosine` | `212` | `15.5%` |
| `negative:excitation` | `188` | `13.7%` |

### Configuration Grid Permutation Metrics

| Cell # | Cosine Thresh | Excitation Thresh | Noise Limit | Mode | Pass Rate | Avg Latency |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `1` | `0.45` | `120` | `3.0` | `positive` | `53.3%` | `57.4ms` |
| `2` | `0.45` | `120` | `4.5` | `positive` | `53.3%` | `50.0ms` |
| `3` | `0.45` | `150` | `3.0` | `positive` | `26.7%` | `51.8ms` |
| `4` | `0.45` | `150` | `4.5` | `positive` | `26.7%` | `55.0ms` |
| `5` | `0.45` | `200` | `3.0` | `positive` | `0.0%` | `50.0ms` |
| `6` | `0.45` | `200` | `4.5` | `positive` | `0.0%` | `50.4ms` |
| `7` | `0.5315` | `120` | `3.0` | `positive` | `6.7%` | `50.2ms` |
| `8` | `0.5315` | `120` | `4.5` | `positive` | `6.7%` | `54.2ms` |
| `9` | `0.5315` | `150` | `3.0` | `positive` | `6.7%` | `54.4ms` |
| `10` | `0.5315` | `150` | `4.5` | `positive` | `6.7%` | `57.3ms` |
| `11` | `0.5315` | `200` | `3.0` | `positive` | `0.0%` | `60.8ms` |
| `12` | `0.5315` | `200` | `4.5` | `positive` | `0.0%` | `65.4ms` |
| `13` | `0.65` | `120` | `3.0` | `positive` | `0.0%` | `62.7ms` |
| `14` | `0.65` | `120` | `4.5` | `positive` | `0.0%` | `51.0ms` |
| `15` | `0.65` | `150` | `3.0` | `positive` | `0.0%` | `57.5ms` |
| `16` | `0.65` | `150` | `4.5` | `positive` | `0.0%` | `59.3ms` |
| `17` | `0.65` | `200` | `3.0` | `positive` | `0.0%` | `63.5ms` |
| `18` | `0.65` | `200` | `4.5` | `positive` | `0.0%` | `54.7ms` |
| `19` | `0.45` | `120` | `3.0` | `negative` | `20.0%` | `59.6ms` |
| `20` | `0.45` | `120` | `4.5` | `negative` | `20.0%` | `59.8ms` |
| `21` | `0.45` | `150` | `3.0` | `negative` | `40.0%` | `61.0ms` |
| `22` | `0.45` | `150` | `4.5` | `negative` | `40.0%` | `65.9ms` |
| `23` | `0.45` | `200` | `3.0` | `negative` | `40.0%` | `54.0ms` |
| `24` | `0.45` | `200` | `4.5` | `negative` | `40.0%` | `52.8ms` |
| `25` | `0.5315` | `120` | `3.0` | `negative` | `40.0%` | `51.2ms` |
| `26` | `0.5315` | `120` | `4.5` | `negative` | `40.0%` | `50.4ms` |
| `27` | `0.5315` | `150` | `3.0` | `negative` | `93.3%` | `46.8ms` |
| `28` | `0.5315` | `150` | `4.5` | `negative` | `93.3%` | `51.0ms` |
| `29` | `0.5315` | `200` | `3.0` | `negative` | `93.3%` | `63.5ms` |
| `30` | `0.5315` | `200` | `4.5` | `negative` | `93.3%` | `61.0ms` |
| `31` | `0.65` | `120` | `3.0` | `negative` | `40.0%` | `60.7ms` |
| `32` | `0.65` | `120` | `4.5` | `negative` | `40.0%` | `67.3ms` |
| `33` | `0.65` | `150` | `3.0` | `negative` | `100.0%` | `74.5ms` |
| `34` | `0.65` | `150` | `4.5` | `negative` | `100.0%` | `62.7ms` |
| `35` | `0.65` | `200` | `3.0` | `negative` | `100.0%` | `55.5ms` |
| `36` | `0.65` | `200` | `4.5` | `negative` | `100.0%` | `69.3ms` |


## Telemetry Traces & Boundary Transition Events

_No sharp boundary transition points detected in this test run._


## Actionable Developer & AI Tuning Recommendations

1. **Cosine Similarity Calibration:**
   - Cosine threshold appears well-balanced for the tested queries.
2. **Excitation Accumulator Sensitivity:**
   - Keep `excitation_threshold` at `150-170` to prevent multi-part prompt bypasses while avoiding legitimate prompt blocking.
3. **Pipeline Evaluation Ordering:**
   - Optimal recommended pipeline sequence: `Cosine (Order 1) -> Entropy Noise (Order 2) -> Excitation (Order 3)` for minimal latency overhead.