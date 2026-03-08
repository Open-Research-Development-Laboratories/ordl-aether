#!/usr/bin/env python3
"""
Generate human-readable documentation artifacts from repo_index.sqlite.
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional


ROOT = Path(__file__).resolve().parent.parent
KB_DIR = ROOT / "docs" / "knowledge-base"
DB_PATH = KB_DIR / "repo_index.sqlite"


@dataclass
class Finding:
    severity: str
    title: str
    file: str
    line: int
    detail: str


def load_file(path: Path) -> List[str]:
    return path.read_text(encoding="utf-8", errors="replace").splitlines()


def find_line(lines: List[str], pattern: str) -> int:
    rx = re.compile(pattern)
    for idx, line in enumerate(lines, start=1):
        if rx.search(line):
            return idx
    return 1


def detect_findings() -> List[Finding]:
    findings: List[Finding] = []

    routes_path = ROOT / "aether-system" / "backend" / "api" / "routes.py"
    routes_lines = load_file(routes_path)
    catch_line = find_line(routes_lines, r"except Exception as e:")
    findings.append(
        Finding(
            severity="P1",
            title="HTTPException statuses are overwritten as 500",
            file="aether-system/backend/api/routes.py",
            line=catch_line,
            detail=(
                "Route handlers raise HTTPException with 400/503, but broad exception "
                "handlers catch them and re-raise 500, masking intended client/server error semantics."
            ),
        )
    )

    ingest_path = ROOT / "aether-system" / "backend" / "modules" / "data_ingestion.py"
    ingest_lines = load_file(ingest_path)
    nasa_url_line = find_line(ingest_lines, r'url = f"\{settings\.NASA_API_KEY\}/planetary/apod"')
    findings.append(
        Finding(
            severity="P1",
            title="NASA APOD endpoint URL is built from API key string",
            file="aether-system/backend/modules/data_ingestion.py",
            line=nasa_url_line,
            detail=(
                "APOD fetch URL uses NASA_API_KEY as host prefix; expected base endpoint is "
                "https://api.nasa.gov/planetary/apod with API key in query params."
            ),
        )
    )

    source_name_line = find_line(ingest_lines, r'"name": "OpenMeteo"')
    weather_switch_line = find_line(ingest_lines, r'elif source_name == "weather"')
    findings.append(
        Finding(
            severity="P2",
            title="Registered source name does not match ingestion switch key",
            file="aether-system/backend/modules/data_ingestion.py",
            line=weather_switch_line,
            detail=(
                "Default source is registered as OpenMeteo but process() checks for source_name == "
                "\"weather\", causing Unknown source if callers use advertised source names."
            ),
        )
    )

    app_path = ROOT / "aether-system" / "frontend" / "src" / "App.jsx"
    app_lines = load_file(app_path)
    base_line = find_line(app_lines, r"axios\.defaults\.baseURL = 'http://localhost:8000/api/v1'")
    health_line = find_line(app_lines, r"axios\.get\('/health'\)")
    findings.append(
        Finding(
            severity="P1",
            title="Frontend health polling points to non-existent prefixed route",
            file="aether-system/frontend/src/App.jsx",
            line=health_line,
            detail=(
                "Base URL is /api/v1, but health endpoint exists at /health (outside router prefix). "
                "Current request resolves to /api/v1/health and will fail."
            ),
        )
    )

    status_path = ROOT / "aether-system" / "frontend" / "src" / "pages" / "SystemStatus.jsx"
    status_lines = load_file(status_path)
    loader_use_line = find_line(status_lines, r"<Loader")
    loader_import_line = find_line(status_lines, r"from 'lucide-react'")
    findings.append(
        Finding(
            severity="P1",
            title="Loader icon is used but not imported",
            file="aether-system/frontend/src/pages/SystemStatus.jsx",
            line=loader_use_line,
            detail=(
                "Component renders <Loader /> during loading state, but Loader is absent from lucide-react imports, "
                "causing runtime ReferenceError."
            ),
        )
    )

    main_path = ROOT / "aether-system" / "backend" / "main.py"
    main_lines = load_file(main_path)
    cors_line = find_line(main_lines, r"allow_origins=settings\.ALLOWED_HOSTS")
    findings.append(
        Finding(
            severity="P2",
            title="Default CORS settings conflict with credentialed requests",
            file="aether-system/backend/main.py",
            line=cors_line,
            detail=(
                "Defaults use allow_origins=['*'] with allow_credentials=True. "
                "FastAPI/Starlette CORS docs state wildcard cannot be combined with credentialed requests."
            ),
        )
    )

    return findings


def write_full_file_ledger(conn: sqlite3.Connection) -> None:
    rows = conn.execute(
        """
        SELECT path, size_bytes, line_count, is_text, sha256
        FROM files
        ORDER BY path
        """
    ).fetchall()

    out = KB_DIR / "full_file_ledger.md"
    lines = [
        "# Full File Ledger",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Files listed: `{len(rows)}`",
        "",
        "Each entry includes path, size, line count (if text), type, and SHA-256.",
        "",
    ]

    for row in rows:
        kind = "text" if row["is_text"] else "binary"
        line_count = row["line_count"] if row["line_count"] is not None else "-"
        lines.append(
            f"- `{row['path']}` | {kind} | {row['size_bytes']} bytes | lines: {line_count} | sha256: {row['sha256'][:16]}"
        )

    out.write_text("\n".join(lines), encoding="utf-8")


def write_architecture_and_findings(conn: sqlite3.Connection) -> None:
    findings = detect_findings()

    # Pull selected symbol sets for quick navigation.
    backend_symbols = conn.execute(
        """
        SELECT path, symbol_type, symbol_name, line_no
        FROM symbols
        WHERE path LIKE 'aether-system/backend/%'
        ORDER BY path, line_no
        """
    ).fetchall()
    frontend_symbols = conn.execute(
        """
        SELECT path, symbol_type, symbol_name, line_no
        FROM symbols
        WHERE path LIKE 'aether-system/frontend/%'
        ORDER BY path, line_no
        """
    ).fetchall()

    routes_file = ROOT / "aether-system" / "backend" / "api" / "routes.py"
    route_lines = load_file(routes_file)
    endpoint_entries = []
    for idx, line in enumerate(route_lines, start=1):
        m = re.search(r'@router\.(get|post|put|delete|patch)\("([^"]+)"\)', line)
        if m:
            endpoint_entries.append((idx, m.group(1).upper(), m.group(2)))

    architecture_path = KB_DIR / "system_architecture.md"
    arch_lines = [
        "# System Architecture",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## Major Areas",
        "",
        "- `aether-system/backend`: FastAPI service, module orchestration, data ingestion, analytics, and knowledge storage.",
        "- `aether-system/frontend`: React + Vite dashboard for analysis workflows and system status.",
        "- `*.md` at repo root: NASA-inspired research corpus and technical concept docs.",
        "- `docs/knowledge-base`: local memory/index artifacts for exhaustive traversal.",
        "",
        "## API Endpoints",
        "",
    ]
    for line_no, method, route in endpoint_entries:
        arch_lines.append(
            f"- `aether-system/backend/api/routes.py:{line_no}` -> `{method} {route}`"
        )

    arch_lines.extend(["", "## Backend Symbols", ""])
    for row in backend_symbols:
        arch_lines.append(
            f"- `{row['path']}:{row['line_no']}` [{row['symbol_type']}] `{row['symbol_name']}`"
        )

    arch_lines.extend(["", "## Frontend Symbols", ""])
    for row in frontend_symbols:
        arch_lines.append(
            f"- `{row['path']}:{row['line_no']}` [{row['symbol_type']}] `{row['symbol_name']}`"
        )

    architecture_path.write_text("\n".join(arch_lines), encoding="utf-8")

    findings_path = KB_DIR / "review_findings.md"
    findings_lines = [
        "# Review Findings",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "Ordered by severity.",
        "",
    ]
    for finding in sorted(findings, key=lambda f: f.severity):
        findings_lines.extend(
            [
                f"## [{finding.severity}] {finding.title}",
                "",
                f"- File: `{finding.file}:{finding.line}`",
                f"- Detail: {finding.detail}",
                "",
            ]
        )
    findings_path.write_text("\n".join(findings_lines), encoding="utf-8")


def write_external_research_note() -> None:
    note_path = KB_DIR / "external_research_notes.md"
    lines = [
        "# External Research Notes",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        "## FastAPI References Used",
        "",
        "- Handling errors guide: https://fastapi.tiangolo.com/tutorial/handling-errors/",
        "- CORS guide: https://fastapi.tiangolo.com/tutorial/cors/",
        "",
        "## Key Guidance Applied",
        "",
        "- `HTTPException` should propagate with its intended status code instead of being wrapped into generic 500 responses.",
        "- With `allow_credentials=True`, wildcard (`*`) should not be used for `allow_origins`.",
        "",
    ]
    note_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    if not DB_PATH.exists():
        raise SystemExit(f"Missing index DB: {DB_PATH}")

    KB_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    try:
        write_full_file_ledger(conn)
        write_architecture_and_findings(conn)
        write_external_research_note()
    finally:
        conn.close()

    print("Generated KB docs in docs/knowledge-base")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
