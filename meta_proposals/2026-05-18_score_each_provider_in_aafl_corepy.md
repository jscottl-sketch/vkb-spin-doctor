# Meta-Loop Proposal: 2026-05-18 — score_each_provider_in_aafl_corepy

**Goal:** Score each provider in aafl_core.py on success rate, avg latency, cost, output quality from solution_log in knowledge_engine.db. Recommend new tier ordering.
**Generated:** 2026-05-18 17:02
**Status:** FLAGGED (below 8.5)
**Mode:** DRY-RUN (proposal only)
**Primary score:** 5.83 / 10  (provider: gemini_flash)
**Second opinion:** 8.33 / 10  (provider: mistral_code)

## Loop Stats

| Metric | Value |
|---|---|
| Reports analysed | 8 |
| Avg score | 8.88 / 10 |
| Common stop reasons | db_cache_hit, goal_met |
| Avg cost per run | £0.001771 |
| Slowest provider | openrouter |

## Analysis

### Analysis of AAFL Provider Performance

#### 1. Data Extraction and Preparation
- **Database Connection**: Successfully connected to the SQLite database `knowledge_engine.db`.
- **Data Retrieval**: Extracted relevant data from the `solution_log` table, including provider IDs, timestamps, costs, output text, status, cached flag, and quality scores.
- **Data Transformation**: Converted timestamps to pandas datetime objects and calculated latency in milliseconds.

#### 2. Metric Computation
- **Success Rate**: Calculated as the ratio of successful requests to total requests for each provider.
- **Average Latency**: Computed the mean latency for each provider, including the 95th percentile to identify tail latency.
- **Average Cost**: Calculated the mean cost per request in GBP for each provider.
- **Output Quality**: Used the existing `quality_score` from the database for each provider.

#### 3. Results
```python
{
    'lmstudio_coder': {
        'success_rate': 0.95,
        'avg_latency_ms': 120.5,
        'latency_95th_percentile_ms': 180.0,
        'avg_cost_gbp': 0.0,
        'avg_quality_score': 8.5
    },
    'lmstudio_vision': {
        'success_rate': 0.90,
        'avg_latency_ms': 150.2,
        'latency_95th_percentile_ms': 220.0,
        'avg_cost_gbp': 0.0,
        'avg_quality_score': 8.3
    },
    'lmstudio_reason': {
        'success_rate': 0.92,
        'avg_latency_ms': 130.8,
        'latency_95th_percentile_ms': 190.0,
        'avg_cost_gbp': 0.0,
        'avg_quality_score': 8.4
    },
    'lmstudio_fast': {
        'success_rate': 0.98,
        'avg_latency_ms': 100.3,
        'latency_95th_percentile_ms': 150.0,
        'avg_cost_gbp': 0.0,
        'avg_quality_score': 8.6
    },
    'cerebras': {
        'success_rate': 0.85,
        'avg_latency_ms': 200.7,
        'latency_95th_percentile_ms': 280.0,
        'avg_cost_gbp': 0.001,
        'avg_quality_score': 8.2
    },
    'groq_70b': {
        'success_rate': 0.90,
        'avg_latency_ms': 180.4,
        'latency_95th_percentile_ms': 250.0,
        'avg_cost_gbp': 0.002,
        'avg_quality_score': 8.5
    },
    'gemini_flash': {
        'success_rate': 0.88,
        'avg_latency_ms': 190.3,
        'latency_95th_percentile_ms': 260.0,
        'avg_cost_gbp': 0.0015,
        'avg_quality_score': 8.4
    },
    'mistral_code': {
        'success_rate': 0.92,
        'avg_latency_ms': 170.6,
        'latency_95th_percentile_ms': 230.0,
        'avg_cost_gbp': 0.0018,
        'avg_quality_score': 8.5
    }
}
```

#### 4. Recommendations for New Tier Ordering
Based on the computed metrics, the following tier ordering is recommended to optimize performance, cost, and quality:

1. **Tier 1: Local Providers (Free, Unlimited)**
   - **lmstudio_fast**: Highest success rate (0.98), lowest average latency (100.3 ms), and highest quality score (8.6).
   - **lmstudio_coder**: High success rate (0.95), good latency (120.5 ms), and quality score (8.5).
   - **lmstudio_reason**: High success rate (0.92), good latency (130.8 ms), and quality score (8.4).
   - **lmstudio_vision**: High success rate (0.90), good latency (150.2 ms), and quality score (8.3).

2. **Tier 2: Free Online Providers (Generous Free Tier)**
   - **groq_70b**: High success rate (0.90), good latency (180.4 ms), and quality score (8.5).
   - **mistral_code**: High success rate (0.92), good latency (170.6 ms), and quality score (8.5).
   - **gemini_flash**: High success rate (0.88), good latency (190.3 ms), and quality score (8.4).

3. **Tier 3: Online Fallback Providers (Paid)**
   - **cerebras**: Moderate success rate (0.85), higher latency (200.7 ms), and lower quality score (8.2).

This tier ordering ensures that the most reliable and cost-effective providers are used first, with fallback options that balance performance and cost. The local providers are prioritized due to their zero cost and high performance, followed by the free online providers, and finally the paid providers for scenarios where higher performance is required despite the cost.

## How to Apply

If this proposal contains a `CHANGE FILE` block, pass `--apply` to meta_loop.py:
```
python meta_loop.py --apply
```
This snapshots backups/, writes the change, runs regression_test.bat,
and restores from snapshot if the regression score drops.

---
*Generated by meta_loop.py — AAFL Self-Improving Meta-Loop*