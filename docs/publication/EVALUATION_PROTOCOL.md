# Evaluation Protocol

## Rules

1. No model promotion without benchmark evidence.
2. Every benchmark run must be reproducible from repo state and input dataset version.
3. Production changes must include before/after metrics for affected tracks.

## Track Metrics

### Text

- Summary quality (human-rated + automated overlap metrics where applicable)
- Entity extraction precision/recall on labeled set
- Sentiment consistency and confidence calibration
- Classification top-1 accuracy for domain labels

### Vision

- Top-k classification accuracy on labeled image set
- Detection precision/recall and confidence calibration
- Embedding retrieval relevance (precision at k)

### Anomaly

- Precision/recall/F1 against labeled anomalies
- False positive rate in normal windows
- Detection latency for change events

## Operational Metrics

- API p50/p95 latency by endpoint
- Error rate by endpoint
- Startup readiness time
- Disk growth rate due to model cache and data artifacts

## Reporting

Every evaluation run should produce:

1. Dataset versions used
2. Exact code ref (commit hash)
3. Runtime configuration summary
4. Metric table (baseline vs candidate)
5. Decision (promote, hold, or reject)

