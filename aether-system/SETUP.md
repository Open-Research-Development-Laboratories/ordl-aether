# AETHER Setup Guide

Back to runtime docs: [README.md](README.md) | [Repository index](../docs/INDEX.md)

## Prerequisites

- Podman installed and available on PATH.
- `podman-compose` available as `python -m podman_compose`.
- At least 4 GB RAM and 10 GB free disk.

## 1. Prepare Environment

```bash
cd aether-system
cp .env.example .env
```

Optionally update API keys and environment values in `.env`.

## 2. Start the Platform

```bash
python -m podman_compose up -d
```

Use rebuild mode when dependencies or container build files change:

```bash
python -m podman_compose up -d --build
```

## 3. Verify Health

- Dashboard: `http://localhost:3000`
- API docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/ready`

## 4. Operational Commands

```bash
# Follow logs
python -m podman_compose logs -f

# Stop services
python -m podman_compose down

# Restart services
python -m podman_compose down
python -m podman_compose up -d
```

## 5. Quality and Security Checks

Run from repository root:

```bash
python scripts/secret_scan.py
python scripts/smoke_test.py
python scripts/benchmark_api.py --requests 40 --concurrency 8
```

## 6. Common Troubleshooting

- Backend not healthy: `python -m podman_compose logs -f backend`
- Frontend unreachable: `python -m podman_compose logs -f frontend`
- Port conflicts: update service ports in `aether-system/docker-compose.yml`
- Slow first start: expected when dependencies or models are downloading

## Related Documents

- [Runtime README](README.md)
- [Project Summary](PROJECT_SUMMARY.md)
- [Cloudflare Tunnel Guide](../docs/cloudflare-tunnel.md)
