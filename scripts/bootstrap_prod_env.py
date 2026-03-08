#!/usr/bin/env python3
"""
Generate a production env file with strong defaults.

Usage:
  python scripts/bootstrap_prod_env.py --domain aether.ordl.org
"""
from __future__ import annotations

import argparse
import secrets
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
AETHER_DIR = REPO_ROOT / "aether-system"
OUTPUT_FILE = AETHER_DIR / ".env.production"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate .env.production for AETHER.")
    parser.add_argument("--domain", required=True, help="Primary public domain (e.g. aether.ordl.org)")
    parser.add_argument(
        "--nasa-api-key",
        default="REPLACE_WITH_REAL_NASA_API_KEY",
        help="NASA API key value (defaults to placeholder)",
    )
    args = parser.parse_args()

    secret_key = secrets.token_urlsafe(64)
    allowed_hosts = ",".join(
        [
            f"https://{args.domain}",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )

    content = "\n".join(
        [
            "# AETHER production environment",
            "ENVIRONMENT=production",
            "DEBUG=false",
            "HOST=0.0.0.0",
            "PORT=8000",
            f"SECRET_KEY={secret_key}",
            f"ALLOWED_HOSTS={allowed_hosts}",
            f"NASA_API_KEY={args.nasa_api_key}",
            "DATABASE_URL=sqlite:///./data/aether.db",
            "VECTOR_DB_PATH=./data/vector_db",
            "MODEL_CACHE_DIR=./ai_models/cache",
            "PREWARM_MODELS=false",
            "REDIS_URL=redis://localhost:6379/0",
            "",
        ]
    )

    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"Generated {OUTPUT_FILE}")
    print("Fill or rotate NASA_API_KEY if still placeholder.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
