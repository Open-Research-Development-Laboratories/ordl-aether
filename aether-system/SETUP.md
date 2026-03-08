# AETHER Setup Guide

## Prerequisites

- Podman
- podman-compose
- 4GB+ RAM
- 10GB free disk

## 1) Configure

```bash
cd aether-system
cp .env.example .env
```

Optional: add your NASA API key in `.env`.

## 2) Start (Podman Compose)

```bash
podman-compose up -d --build
```

First run may take a while due to dependency/model downloads.

## 3) Verify

- Dashboard: http://localhost:3000
- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Common Commands

```bash
# Stream logs
podman-compose logs -f

# Restart
podman-compose down
podman-compose up -d --build

# Stop
podman-compose down
```

## Project Layout

```text
aether-system/
|-- backend/
|-- frontend/
|-- data/
|-- ai_models/
|-- docker-compose.yml
|-- start.sh
`-- .env.example
```

## Manual Development (No Compose)

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

## Troubleshooting

- Backend not healthy: `podman-compose logs -f backend`
- Frontend not reachable: `podman-compose logs -f frontend`
- Port conflict: change ports in `docker-compose.yml`
