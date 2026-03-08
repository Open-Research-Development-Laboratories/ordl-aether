#!/usr/bin/env python3
"""
Build a local, full-repo knowledge index.

Outputs:
- docs/knowledge-base/repo_index.sqlite (metadata + FTS content index)
- docs/knowledge-base/repo_manifest.json (full file manifest)
- docs/knowledge-base/file_index.csv (easy spreadsheet export)
- docs/knowledge-base/knowledge_base_overview.md (human summary)
- docs/knowledge-base/doc_catalog.md (markdown document catalog)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import sqlite3
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


PY_SYMBOL_RE = re.compile(r"^\s*(?:async\s+def|def|class)\s+([A-Za-z_][A-Za-z0-9_]*)")
JS_SYMBOL_RE = re.compile(
    r"^\s*(?:export\s+)?(?:async\s+)?(?:function|class)\s+([A-Za-z_$][A-Za-z0-9_$]*)"
)
JS_CONST_RE = re.compile(r"^\s*(?:export\s+)?const\s+([A-Za-z_$][A-Za-z0-9_$]*)\s*=")
MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$")


@dataclass
class FileRecord:
    path: str
    size_bytes: int
    sha256: str
    modified_utc: str
    is_text: bool
    encoding: Optional[str]
    line_count: Optional[int]
    scan_error: Optional[str]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build local repo knowledge index")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument(
        "--output-dir", default="docs/knowledge-base", help="Output directory"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=5000,
        help="Approximate max chars per text chunk",
    )
    return parser.parse_args()


def should_skip_dir(dir_name: str, rel_path: str, output_dir_rel: str) -> bool:
    if rel_path == output_dir_rel:
        return True
    if rel_path.startswith(output_dir_rel + "/"):
        return True
    return False


def iter_repo_files(root: Path, output_dir_rel: str) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dir_path = Path(dirpath)
        rel_dir = dir_path.relative_to(root).as_posix() if dir_path != root else ""

        kept_dirs = []
        for name in dirnames:
            child_rel = f"{rel_dir}/{name}" if rel_dir else name
            if should_skip_dir(name, child_rel, output_dir_rel):
                continue
            kept_dirs.append(name)
        dirnames[:] = kept_dirs

        for filename in filenames:
            yield dir_path / filename


def decode_text(raw: bytes) -> Tuple[bool, Optional[str], Optional[str]]:
    if b"\x00" in raw:
        return False, None, None

    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            text = raw.decode(encoding)
        except UnicodeDecodeError:
            continue

        if encoding == "latin-1":
            sample = text[:2000]
            if sample:
                printable = sum(
                    1 for ch in sample if ch.isprintable() or ch in "\n\r\t"
                )
                if printable / len(sample) < 0.85:
                    continue
        return True, encoding, text

    return False, None, None


def chunk_text(text: str, max_chars: int) -> List[Tuple[int, int, str]]:
    lines = text.splitlines()
    if not lines:
        return []

    chunks: List[Tuple[int, int, str]] = []
    current: List[str] = []
    current_len = 0
    start_line = 1

    for line_no, line in enumerate(lines, start=1):
        segment = line + "\n"
        if current and current_len + len(segment) > max_chars:
            chunks.append((start_line, line_no - 1, "".join(current)))
            current = [segment]
            current_len = len(segment)
            start_line = line_no
        else:
            current.append(segment)
            current_len += len(segment)

    if current:
        chunks.append((start_line, len(lines), "".join(current)))

    return chunks


def extract_symbols(path: str, text: str) -> List[Tuple[str, str, int]]:
    suffix = Path(path).suffix.lower()
    symbols: List[Tuple[str, str, int]] = []

    for line_no, line in enumerate(text.splitlines(), start=1):
        if suffix == ".py":
            m = PY_SYMBOL_RE.match(line)
            if m:
                name = m.group(1)
                symbol_type = "class" if line.lstrip().startswith("class ") else "function"
                symbols.append((symbol_type, name, line_no))
        elif suffix in {".js", ".jsx", ".ts", ".tsx"}:
            m = JS_SYMBOL_RE.match(line)
            if m:
                keyword = "class" if "class" in line else "function"
                symbols.append((keyword, m.group(1), line_no))
            else:
                c = JS_CONST_RE.match(line)
                if c:
                    symbols.append(("const", c.group(1), line_no))
        elif suffix == ".md":
            h = MD_HEADING_RE.match(line)
            if h:
                level = len(h.group(1))
                symbols.append((f"heading_h{level}", h.group(2).strip(), line_no))

    return symbols


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS files (
            path TEXT PRIMARY KEY,
            size_bytes INTEGER NOT NULL,
            sha256 TEXT NOT NULL,
            modified_utc TEXT NOT NULL,
            is_text INTEGER NOT NULL,
            encoding TEXT,
            line_count INTEGER,
            scan_error TEXT
        );

        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            chunk_index INTEGER NOT NULL,
            start_line INTEGER NOT NULL,
            end_line INTEGER NOT NULL,
            content TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS symbols (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path TEXT NOT NULL,
            symbol_type TEXT NOT NULL,
            symbol_name TEXT NOT NULL,
            line_no INTEGER NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_chunks_path ON chunks(path);
        CREATE INDEX IF NOT EXISTS idx_symbols_path ON symbols(path);
        CREATE INDEX IF NOT EXISTS idx_symbols_name ON symbols(symbol_name);

        CREATE VIRTUAL TABLE IF NOT EXISTS content_fts
        USING fts5(path, content, tokenize='porter unicode61');
        """
    )


def clear_index(conn: sqlite3.Connection) -> None:
    conn.execute("DELETE FROM files")
    conn.execute("DELETE FROM chunks")
    conn.execute("DELETE FROM symbols")
    conn.execute("DELETE FROM content_fts")
    conn.commit()


def get_first_heading(markdown_text: str) -> Optional[str]:
    for line in markdown_text.splitlines():
        m = MD_HEADING_RE.match(line)
        if m:
            return m.group(2).strip()
    return None


def write_outputs(
    output_dir: Path,
    records: List[FileRecord],
    ext_counts: Counter,
    dir_counts: Counter,
    largest_files: List[FileRecord],
    markdown_catalog: List[Tuple[str, Optional[str]]],
) -> None:
    manifest_path = output_dir / "repo_manifest.json"
    csv_path = output_dir / "file_index.csv"
    overview_path = output_dir / "knowledge_base_overview.md"
    doc_catalog_path = output_dir / "doc_catalog.md"

    total_size = sum(r.size_bytes for r in records)
    text_files = sum(1 for r in records if r.is_text)
    binary_files = len(records) - text_files

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "total_files": len(records),
        "total_size_bytes": total_size,
        "text_files": text_files,
        "binary_files": binary_files,
        "files": [r.__dict__ for r in records],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "path",
                "size_bytes",
                "sha256",
                "modified_utc",
                "is_text",
                "encoding",
                "line_count",
                "scan_error",
            ]
        )
        for r in records:
            writer.writerow(
                [
                    r.path,
                    r.size_bytes,
                    r.sha256,
                    r.modified_utc,
                    int(r.is_text),
                    r.encoding or "",
                    r.line_count if r.line_count is not None else "",
                    r.scan_error or "",
                ]
            )

    top_ext = ext_counts.most_common(15)
    top_dirs = dir_counts.most_common(20)
    overview_lines = [
        "# Knowledge Base Overview",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Total files indexed: `{len(records)}`",
        f"- Text files: `{text_files}`",
        f"- Binary files: `{binary_files}`",
        f"- Total size: `{total_size}` bytes",
        "",
        "## Top Extensions",
        "",
    ]
    for ext, count in top_ext:
        label = ext if ext else "[no extension]"
        overview_lines.append(f"- `{label}`: {count}")

    overview_lines.extend(["", "## Largest Files", ""])
    for r in largest_files[:20]:
        overview_lines.append(f"- `{r.path}` ({r.size_bytes} bytes)")

    overview_lines.extend(["", "## Top Directories", ""])
    for d, count in top_dirs:
        label = d if d else "."
        overview_lines.append(f"- `{label}`: {count} files")

    overview_lines.extend(
        [
            "",
            "## Query Commands",
            "",
            "```bash",
            "python scripts/query_knowledge_index.py search \"your query\"",
            "python scripts/query_knowledge_index.py file path/to/file.py",
            "python scripts/query_knowledge_index.py symbols module_name",
            "```",
            "",
        ]
    )
    overview_path.write_text("\n".join(overview_lines), encoding="utf-8")

    doc_lines = [
        "# Markdown Document Catalog",
        "",
        f"- Generated: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Markdown files: `{len(markdown_catalog)}`",
        "",
    ]
    for path, heading in markdown_catalog:
        if heading:
            doc_lines.append(f"- `{path}` -> {heading}")
        else:
            doc_lines.append(f"- `{path}`")
    doc_catalog_path.write_text("\n".join(doc_lines), encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    output_dir = (root / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_dir_rel = output_dir.relative_to(root).as_posix()

    db_path = output_dir / "repo_index.sqlite"
    conn = sqlite3.connect(str(db_path))
    ensure_schema(conn)
    clear_index(conn)

    records: List[FileRecord] = []
    ext_counts: Counter = Counter()
    dir_counts: Counter = Counter()
    markdown_catalog: List[Tuple[str, Optional[str]]] = []

    for abs_path in sorted(iter_repo_files(root, output_dir_rel)):
        rel_path = abs_path.relative_to(root).as_posix()
        ext_counts[Path(rel_path).suffix.lower()] += 1
        dir_counts[str(Path(rel_path).parent).replace("\\", "/")] += 1

        try:
            raw = abs_path.read_bytes()
            size_bytes = len(raw)
            sha256 = hashlib.sha256(raw).hexdigest()
            mtime = datetime.fromtimestamp(
                abs_path.stat().st_mtime, tz=timezone.utc
            ).isoformat()
            is_text, encoding, decoded_text = decode_text(raw)
            line_count = decoded_text.count("\n") + 1 if decoded_text is not None else None

            record = FileRecord(
                path=rel_path,
                size_bytes=size_bytes,
                sha256=sha256,
                modified_utc=mtime,
                is_text=is_text,
                encoding=encoding,
                line_count=line_count,
                scan_error=None,
            )
            records.append(record)

            conn.execute(
                """
                INSERT INTO files(path, size_bytes, sha256, modified_utc, is_text, encoding, line_count, scan_error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.path,
                    record.size_bytes,
                    record.sha256,
                    record.modified_utc,
                    int(record.is_text),
                    record.encoding,
                    record.line_count,
                    record.scan_error,
                ),
            )

            if is_text and decoded_text is not None:
                chunks = chunk_text(decoded_text, args.chunk_size)
                for idx, (start_line, end_line, chunk_content) in enumerate(chunks):
                    conn.execute(
                        """
                        INSERT INTO chunks(path, chunk_index, start_line, end_line, content)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (rel_path, idx, start_line, end_line, chunk_content),
                    )
                    conn.execute(
                        "INSERT INTO content_fts(path, content) VALUES (?, ?)",
                        (rel_path, chunk_content),
                    )

                for symbol_type, symbol_name, line_no in extract_symbols(
                    rel_path, decoded_text
                ):
                    conn.execute(
                        """
                        INSERT INTO symbols(path, symbol_type, symbol_name, line_no)
                        VALUES (?, ?, ?, ?)
                        """,
                        (rel_path, symbol_type, symbol_name, line_no),
                    )

                if Path(rel_path).suffix.lower() == ".md":
                    markdown_catalog.append((rel_path, get_first_heading(decoded_text)))

        except Exception as exc:
            mtime = datetime.now(timezone.utc).isoformat()
            record = FileRecord(
                path=rel_path,
                size_bytes=0,
                sha256="",
                modified_utc=mtime,
                is_text=False,
                encoding=None,
                line_count=None,
                scan_error=str(exc),
            )
            records.append(record)
            conn.execute(
                """
                INSERT INTO files(path, size_bytes, sha256, modified_utc, is_text, encoding, line_count, scan_error)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.path,
                    record.size_bytes,
                    record.sha256,
                    record.modified_utc,
                    int(record.is_text),
                    record.encoding,
                    record.line_count,
                    record.scan_error,
                ),
            )

    conn.commit()
    conn.close()

    largest_files = sorted(records, key=lambda r: r.size_bytes, reverse=True)
    write_outputs(
        output_dir=output_dir,
        records=records,
        ext_counts=ext_counts,
        dir_counts=dir_counts,
        largest_files=largest_files,
        markdown_catalog=sorted(markdown_catalog, key=lambda x: x[0]),
    )

    print(f"Indexed {len(records)} files into {db_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
