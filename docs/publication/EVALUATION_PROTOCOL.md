# Evaluation Protocol

Back to index: [../INDEX.md](../INDEX.md) | [Publication Program](README.md)

## Evaluation Rules

1. No model promotion without benchmark evidence.
2. Every benchmark run must be reproducible from repository state and dataset version.
3. Production-impacting changes must include before and after metrics.

## Track Metrics

### Text

- Summary quality on designated benchmark sets.
- Entity extraction precision and recall on labeled corpora.
- Sentiment consistency and confidence calibration.
- Classification accuracy for target domain labels.

### Vision

- Top-k classification accuracy on labeled image sets.
- Detection precision and recall with confidence calibration.
- Embedding retrieval relevance measured at k.

### Anomaly

- Precision, recall, and F1 against labeled anomalies.
- False positive rate within normal windows.
- Detection latency for known event transitions.

## Operational Metrics

- API latency by endpoint (p50 and p95).
- Endpoint error rate.
- Startup readiness time.
- Disk growth rate from data and model artifacts.

## Required Reporting Fields

Each evaluation record should include:

1. Dataset versions.
2. Exact code reference (commit hash).
3. Runtime configuration summary.
4. Metric table for baseline vs candidate.
5. Promotion decision: promote, hold, or reject.

## Related Documents

- [R&D Program Map](RD_PROGRAM_MAP.md)
- [Model Card Template](MODEL_CARD_TEMPLATE.md)
- [Release Notes Template](RELEASE_NOTES_TEMPLATE.md)
