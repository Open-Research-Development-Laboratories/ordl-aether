# ordl-aether

Main app: `aether-system/`

## External Access

Cloudflare tunnel/domain target:

- `aether.ordl.org`
- recommended tunnel name: `ordl-aether`
- setup guide: [docs/cloudflare-tunnel.md](docs/cloudflare-tunnel.md)

## Security Gate

Before push:

```bash
python scripts/secret_scan.py
```

Optional local pre-push hook install (PowerShell):

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\install_pre_push_hook.ps1
```

## Operations

Smoke test:

```bash
python scripts/smoke_test.py
```

Benchmark baseline:

```bash
python scripts/benchmark_api.py --requests 40 --concurrency 8
```

Generate production env with strong secret:

```bash
python scripts/bootstrap_prod_env.py --domain aether.ordl.org
```

## R&D Publication

Publication ground:

- [docs/publication/README.md](docs/publication/README.md)
- [docs/publication/WHITEPAPER_DRAFT.md](docs/publication/WHITEPAPER_DRAFT.md)

Ingest ORDL docs + current AI research:

```bash
python scripts/ingest_corpora.py
```
