#!/usr/bin/env python3
"""
Lightweight secret scan for local pre-push safety.

Usage:
  python scripts/secret_scan.py
"""
from __future__ import annotations

import fnmatch
import os
import re
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent

# High-signal patterns only; avoid generic keyword noise.
SECRET_PATTERNS = [
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "Private key block"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key"),
    (re.compile(r"\bghp_[A-Za-z0-9]{36}\b"), "GitHub token"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"\bAIza[0-9A-Za-z\-_]{35}\b"), "Google API key"),
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "OpenAI-style key"),
    (
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
        "JWT token",
    ),
    (
        re.compile(
            r"(?i)\b(api[_-]?key|secret|token|password)\b\s*[:=]\s*[\"']?[A-Za-z0-9_/\-+=]{20,}[\"']?"
        ),
        "Potential hardcoded secret assignment",
    ),
]

ALLOWLIST_FRAGMENTS = {
    "DEMO_KEY",
    "your-secret-key",
    "your-secret-key-here-change-in-production",
    "change-in-production",
    "example",
    "placeholder",
}

SKIP_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".pytest_cache",
    "ai_models",
    "data",
}

SKIP_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".pdf",
    ".zip",
    ".tar",
    ".gz",
    ".7z",
    ".pyc",
    ".pyo",
    ".lock",
    ".db",
    ".sqlite",
    ".sqlite3",
}

FORBIDDEN_TRACKED_PATTERNS = [
    ".env",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "*.jks",
    "id_rsa",
    "id_ed25519",
]


def is_binary(path: Path) -> bool:
    try:
        with path.open("rb") as handle:
            chunk = handle.read(2048)
        return b"\x00" in chunk
    except OSError:
        return True


def iter_files(root: Path):
    for current_root, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for filename in files:
            path = Path(current_root) / filename
            if path.suffix.lower() in SKIP_EXTENSIONS:
                continue
            if path.name == ".env.example":
                continue
            yield path


def scan_files() -> list[tuple[Path, int, str, str]]:
    findings: list[tuple[Path, int, str, str]] = []
    for path in iter_files(REPO_ROOT):
        if is_binary(path):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for idx, line in enumerate(content.splitlines(), start=1):
            if any(fragment in line for fragment in ALLOWLIST_FRAGMENTS):
                continue
            for pattern, label in SECRET_PATTERNS:
                if pattern.search(line):
                    findings.append((path, idx, label, line.strip()))
                    break
    return findings


def tracked_forbidden_files() -> list[str]:
    try:
        proc = subprocess.run(
            ["git", "-C", str(REPO_ROOT), "ls-files"],
            check=True,
            text=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError:
        return []
    tracked = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
    bad: list[str] = []
    for path in tracked:
        base = Path(path).name
        for pattern in FORBIDDEN_TRACKED_PATTERNS:
            if fnmatch.fnmatch(base, pattern):
                bad.append(path)
                break
    return bad


def main() -> int:
    forbidden = tracked_forbidden_files()
    findings = scan_files()

    if not forbidden and not findings:
        print("Secret scan passed: no leaked secrets detected.")
        return 0

    if forbidden:
        print("Tracked sensitive file(s) detected:")
        for item in forbidden:
            print(f"  - {item}")

    if findings:
        print("Potential secret findings:")
        for path, line_no, label, line in findings:
            rel = path.relative_to(REPO_ROOT)
            print(f"  - {rel}:{line_no} [{label}] {line[:160]}")

    print("Secret scan failed.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

