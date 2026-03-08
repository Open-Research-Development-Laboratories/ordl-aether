# AETHER - Adaptive Earth & Technology Harmonization Engine

A NASA-inspired unified AI system for data intelligence, pattern recognition, and autonomous analysis.

## What It Includes

- FastAPI backend with modular AI processing
- React frontend dashboard (Vite)
- Hybrid knowledge storage (SQLite + ChromaDB)
- Optional Redis sidecar
- Podman Compose orchestration

## Architecture

```text
aether-system/
|-- backend/                 # FastAPI + AI engine
|   |-- core/
|   |-- modules/
|   |-- knowledge/
|   `-- api/
|-- frontend/                # React dashboard
|   `-- src/
|-- data/                    # Runtime data (created on run)
|-- ai_models/               # Model cache (created on run)
|-- docker-compose.yml       # Podman Compose orchestration
|-- start.sh                 # Quick start helper
`-- .env.example
```

## Quick Start (Podman Compose)

```bash
cd aether-system
cp .env.example .env
python -m podman_compose up -d
```

Rebuild only when dependencies or container build files change:

```bash
python -m podman_compose up -d --build
```

External access is designed for the public host `aether.ordl.org`.
Frontend proxies API routes to backend, so one public hostname is enough.

Access:

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Stop / Logs

```bash
python -m podman_compose logs -f
python -m podman_compose down
```

## Security / Safe Push

- Never commit `.env` or private keys.
- Keep `.env.example` as placeholders only.
- Default CORS is locked to local dashboard origins.

Run the local secret gate before pushing:

```bash
python ../scripts/secret_scan.py
```

Optional pre-push hook install (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File ..\scripts\install_pre_push_hook.ps1
```

Smoke test (full API + UI checks):

```bash
python ../scripts/smoke_test.py
```

Quick benchmark baseline:

```bash
python ../scripts/benchmark_api.py --requests 40 --concurrency 8
```

## Manual Development

Backend:

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Frontend:

```bash
cd frontend
npm install
npm run dev -- --host 0.0.0.0 --port 3000
```
