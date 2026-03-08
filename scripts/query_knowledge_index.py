#!/usr/bin/env python3
"""
Query helper for docs/knowledge-base/repo_index.sqlite.
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path


DEFAULT_DB = Path("docs/knowledge-base/repo_index.sqlite")


def get_conn(db_path: Path) -> sqlite3.Connection:
    if not db_path.exists():
        raise SystemExit(f"Index DB not found: {db_path}")
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def safe_print(text: str) -> None:
    encoding = sys.stdout.encoding or "utf-8"
    encoded = text.encode(encoding, errors="backslashreplace")
    print(encoded.decode(encoding))


def cmd_search(conn: sqlite3.Connection, query: str, limit: int) -> int:
    rows = conn.execute(
        """
        SELECT path, snippet(content_fts, 1, '[', ']', ' ... ', 16) AS snippet
        FROM content_fts
        WHERE content_fts MATCH ?
        LIMIT ?
        """,
        (query, limit),
    ).fetchall()
    if not rows:
        print("No matches.")
        return 0
    for row in rows:
        safe_print(f"{row['path']}: {row['snippet']}")
    return 0


def cmd_file(conn: sqlite3.Connection, path: str, limit: int) -> int:
    norm = path.replace("\\", "/")
    file_row = conn.execute(
        """
        SELECT path, size_bytes, sha256, modified_utc, is_text, encoding, line_count, scan_error
        FROM files
        WHERE path = ?
        """,
        (norm,),
    ).fetchone()

    if not file_row:
        print("File not found in index.")
        return 1

    safe_print(f"path: {file_row['path']}")
    safe_print(f"size_bytes: {file_row['size_bytes']}")
    safe_print(f"sha256: {file_row['sha256']}")
    safe_print(f"modified_utc: {file_row['modified_utc']}")
    safe_print(f"is_text: {bool(file_row['is_text'])}")
    safe_print(f"encoding: {file_row['encoding']}")
    safe_print(f"line_count: {file_row['line_count']}")
    if file_row["scan_error"]:
        safe_print(f"scan_error: {file_row['scan_error']}")

    if file_row["is_text"]:
        chunk_rows = conn.execute(
            """
            SELECT start_line, end_line, content
            FROM chunks
            WHERE path = ?
            ORDER BY chunk_index
            LIMIT ?
            """,
            (norm, limit),
        ).fetchall()
        safe_print("")
        safe_print(f"chunks_shown: {len(chunk_rows)}")
        for row in chunk_rows:
            safe_print(f"\n--- lines {row['start_line']}-{row['end_line']} ---")
            safe_print(row["content"])
    return 0


def cmd_symbols(conn: sqlite3.Connection, pattern: str, limit: int) -> int:
    like = f"%{pattern}%"
    rows = conn.execute(
        """
        SELECT path, symbol_type, symbol_name, line_no
        FROM symbols
        WHERE symbol_name LIKE ?
        ORDER BY path, line_no
        LIMIT ?
        """,
        (like, limit),
    ).fetchall()
    if not rows:
        print("No symbols matched.")
        return 0
    for row in rows:
        safe_print(
            f"{row['path']}:{row['line_no']} [{row['symbol_type']}] {row['symbol_name']}"
        )
    return 0


def cmd_stats(conn: sqlite3.Connection) -> int:
    total_files = conn.execute("SELECT COUNT(*) FROM files").fetchone()[0]
    text_files = conn.execute("SELECT COUNT(*) FROM files WHERE is_text = 1").fetchone()[0]
    binary_files = total_files - text_files
    total_chunks = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    total_symbols = conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0]
    safe_print(f"total_files: {total_files}")
    safe_print(f"text_files: {text_files}")
    safe_print(f"binary_files: {binary_files}")
    safe_print(f"text_chunks: {total_chunks}")
    safe_print(f"symbols: {total_symbols}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Query local knowledge index")
    parser.add_argument("--db", default=str(DEFAULT_DB), help="Path to sqlite index db")
    sub = parser.add_subparsers(dest="command", required=True)

    s = sub.add_parser("search", help="Full-text search")
    s.add_argument("query", help='FTS query string, e.g. "FastAPI AND startup"')
    s.add_argument("--limit", type=int, default=10)

    f = sub.add_parser("file", help="Show file metadata and first chunks")
    f.add_argument("path", help="Repo-relative file path")
    f.add_argument("--limit", type=int, default=2)

    sym = sub.add_parser("symbols", help="Search indexed symbols")
    sym.add_argument("pattern", help="Substring to match symbol names")
    sym.add_argument("--limit", type=int, default=50)

    sub.add_parser("stats", help="Index stats")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    conn = get_conn(Path(args.db))
    try:
        if args.command == "search":
            return cmd_search(conn, args.query, args.limit)
        if args.command == "file":
            return cmd_file(conn, args.path, args.limit)
        if args.command == "symbols":
            return cmd_symbols(conn, args.pattern, args.limit)
        if args.command == "stats":
            return cmd_stats(conn)
    finally:
        conn.close()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
