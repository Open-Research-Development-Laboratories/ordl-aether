# AETHER Runtime Platform

Back to repository index: [../docs/INDEX.md](../docs/INDEX.md) | [Repository Overview](../README.md)

AETHER is the runtime implementation layer for the ORDL research platform. It provides operational APIs, modular intelligence services, and a deployable frontend experience.

## Runtime Scope

- FastAPI backend with modular AI services.
- React frontend for analysis and system operations.
- Persistent data and model cache directories.
- Podman Compose orchestration for reproducible local deployment.

## System Components

### Backend

- API routes for health, status, inference, events, and knowledge search.
- Intelligence modules for text, image, anomaly, and ingestion workflows.
- Knowledge layer for structured storage and retrieval.

### Frontend

- Dashboard for system visibility and status.
- Workflows for text, image, anomaly, and knowledge analysis.
- System status views for module state and event telemetry.

### Runtime Infrastructure

- `docker-compose.yml` used by `podman-compose` workflows.
- Bind-mounted data and model cache volumes for persistence.
- Environment-driven configuration via `.env`.

## Quick Start

```bash
cd aether-system
cp .env.example .env
python -m podman_compose up -d
```

Rebuild when dependencies or container definitions change:

```bash
python -m podman_compose up -d --build
```

## Access Points

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health endpoint: `http://localhost:8000/health`
- Readiness endpoint: `http://localhost:8000/ready`

## Operations

```bash
python -m podman_compose logs -f
python -m podman_compose down
```

## Security and Quality Gates

- Secret scan: `python ../scripts/secret_scan.py`
- Smoke test: `python ../scripts/smoke_test.py`
- Benchmark baseline: `python ../scripts/benchmark_api.py --requests 40 --concurrency 8`

## Related Documents

- [Project Summary](PROJECT_SUMMARY.md)
- [Setup Guide](SETUP.md)
- [ORDL AETHER Research White Paper](../docs/research/white-paper/ordl-aether-research-white-paper.md)
- [Publication Program](../docs/publication/README.md)
