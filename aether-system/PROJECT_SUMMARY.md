# AETHER Project Summary

## Overview

AETHER (Adaptive Earth & Technology Harmonization Engine) is a NASA-inspired AI platform with a modular FastAPI backend and React frontend.

## Core System

- Data ingestion module for external sources and files
- Image analysis module (classification, detection, embeddings)
- Text intelligence module (summary, entities, sentiment, classification)
- Anomaly detection module (statistical + ML ensemble)
- Hybrid knowledge layer (SQLite + vector search)
- Event bus and scheduler for orchestration

## Runtime Model

- `backend` service: FastAPI API on port `8000`
- `frontend` service: Vite UI on port `3000`
- `redis` service: optional sidecar
- Orchestration: `podman-compose`

## Quick Run

```bash
cd aether-system
cp .env.example .env
podman-compose up -d --build
```

## Access

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Skills Demonstrated

- Modular backend architecture
- Multi-model AI integration
- Async API design
- Frontend state-driven dashboards
- Containerized local orchestration with Podman Compose
