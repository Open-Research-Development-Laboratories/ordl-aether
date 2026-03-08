# ORDL Publication Ground

This directory is the public R&D surface for the ORDL AETHER program.

## Purpose

- Publish technical work as reproducible engineering artifacts.
- Track experiments, evaluations, and model performance over time.
- Keep architecture and research outputs aligned with shipped code.

## Structure

- `WHITEPAPER_DRAFT.md` - primary technical narrative.
- `RD_PROGRAM_MAP.md` - active tracks and milestones.
- `EVALUATION_PROTOCOL.md` - benchmark and evaluation rules.
- `MODEL_CARD_TEMPLATE.md` - model transparency template.
- `RELEASE_NOTES_TEMPLATE.md` - release write-up template.
- `RESEARCH_LOG_TEMPLATE.md` - per-experiment logging template.
- `ingestion/` - machine-generated ingestion reports and manifests.

## Ingestion

Use the unified ingestor to capture company docs and recent AI research:

```bash
python scripts/ingest_corpora.py
```

Example with larger research window:

```bash
python scripts/ingest_corpora.py --arxiv-days 365 --arxiv-max-records 5000
```

