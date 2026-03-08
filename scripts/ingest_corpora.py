#!/usr/bin/env python3
"""
Ingest local ORDL docs and current AI research into the AETHER knowledge DB.

This script writes directly to SQLite using the same `knowledge_items` table
schema used by the backend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
import ssl
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_LOCAL_DOCS = Path(r"C:\Users\Winsock\Documents\ORDL Docs")
DEFAULT_DB_PATH = REPO_ROOT / "aether-system" / "data" / "aether.db"
DEFAULT_REPORT_DIR = REPO_ROOT / "docs" / "publication" / "ingestion"

TEXT_EXTENSIONS = {
    ".txt",
    ".md",
    ".csv",
    ".json",
    ".yaml",
    ".yml",
    ".xml",
    ".html",
    ".htm",
    ".py",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".css",
    ".sql",
    ".log",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tif", ".tiff"}
PDF_EXTENSION = ".pdf"
ARXIV_API_URL = "http://export.arxiv.org/api/query"
ARXIV_CATEGORY_QUERY = (
    "cat:cs.AI OR cat:cs.CL OR cat:cs.CV OR cat:cs.LG OR cat:stat.ML OR cat:cs.RO OR cat:cs.IR"
)


@dataclass
class LocalDocRecord:
    title: str
    item_type: str
    content: str
    metadata: Dict[str, Any]


@dataclass
class ArxivRecord:
    title: str
    content: str
    metadata: Dict[str, Any]


class KnowledgeWriter:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def __enter__(self) -> "KnowledgeWriter":
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self._ensure_schema()
        return self

    def __exit__(self, exc_type, exc, tb):
        if self.conn is not None:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def _ensure_schema(self):
        assert self.conn is not None
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS knowledge_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_type VARCHAR(50) NOT NULL,
                title VARCHAR(500),
                content TEXT,
                source VARCHAR(255),
                metadata_json TEXT,
                embedding_id VARCHAR(255),
                confidence FLOAT,
                created_at DATETIME,
                updated_at DATETIME
            )
            """
        )
        self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_knowledge_source_title ON knowledge_items(source, title)"
        )
        self.conn.commit()

    def existing_titles(self, source: str) -> set[str]:
        assert self.conn is not None
        rows = self.conn.execute(
            "SELECT title FROM knowledge_items WHERE source = ?",
            (source,),
        ).fetchall()
        return {row["title"] for row in rows if row["title"]}

    def insert_item(
        self,
        item_type: str,
        title: str,
        content: str,
        source: str,
        metadata: Dict[str, Any],
        confidence: float = 1.0,
    ) -> int:
        assert self.conn is not None
        now = datetime.now(timezone.utc).isoformat()
        cursor = self.conn.execute(
            """
            INSERT INTO knowledge_items (
                item_type, title, content, source, metadata_json, embedding_id,
                confidence, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_type,
                title,
                content,
                source,
                json.dumps(metadata, ensure_ascii=True),
                None,
                confidence,
                now,
                now,
            ),
        )
        self.conn.commit()
        return int(cursor.lastrowid)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest ORDL docs + AI research into AETHER knowledge DB")
    parser.add_argument("--db-path", default=str(DEFAULT_DB_PATH), help="Path to sqlite DB")
    parser.add_argument("--local-docs-root", default=str(DEFAULT_LOCAL_DOCS), help="Path to local ORDL docs")
    parser.add_argument("--skip-local-docs", action="store_true", help="Skip local docs ingestion")
    parser.add_argument("--skip-arxiv", action="store_true", help="Skip arXiv AI research ingestion")
    parser.add_argument("--arxiv-days", type=int, default=120, help="Recent window for arXiv ingestion")
    parser.add_argument("--arxiv-query", default=ARXIV_CATEGORY_QUERY, help="arXiv search query")
    parser.add_argument(
        "--arxiv-window-days",
        type=int,
        default=14,
        help="Window size for date-sliced arXiv ingestion (set 0 to disable)",
    )
    parser.add_argument("--arxiv-page-size", type=int, default=100, help="arXiv page size")
    parser.add_argument("--arxiv-max-records", type=int, default=2500, help="Max arXiv records per run")
    parser.add_argument("--arxiv-start", type=int, default=0, help="Start offset for arXiv pagination")
    parser.add_argument("--report-dir", default=str(DEFAULT_REPORT_DIR), help="Directory for ingestion reports")
    return parser.parse_args()


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def format_arxiv_datetime(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y%m%d%H%M")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_text_bytes(data: bytes) -> Tuple[str, str]:
    for encoding in ("utf-8", "utf-16", "latin-1"):
        try:
            return data.decode(encoding), encoding
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace"), "utf-8-replace"


def extract_pdf_text(path: Path) -> Tuple[str, Dict[str, Any]]:
    metadata: Dict[str, Any] = {}
    try:
        from pypdf import PdfReader
    except Exception as exc:
        metadata["extract_error"] = f"pypdf unavailable: {exc}"
        return "", metadata

    reader = PdfReader(str(path))
    pages: List[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages.append(text)

    metadata["page_count"] = len(reader.pages)
    metadata["extracted_characters"] = sum(len(page) for page in pages)
    return "\n\n".join(pages), metadata


def extract_image_metadata(path: Path) -> Dict[str, Any]:
    try:
        from PIL import Image
    except Exception as exc:
        return {"extract_error": f"Pillow unavailable: {exc}"}

    with Image.open(path) as img:
        return {
            "width": img.width,
            "height": img.height,
            "mode": img.mode,
            "format": img.format,
        }


def build_local_doc_record(path: Path, root: Path) -> LocalDocRecord:
    rel_path = path.relative_to(root).as_posix()
    raw = path.read_bytes()
    file_sha = sha256_bytes(raw)
    extension = path.suffix.lower()
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()

    base_metadata: Dict[str, Any] = {
        "path": rel_path,
        "filename": path.name,
        "extension": extension,
        "size_bytes": len(raw),
        "sha256": file_sha,
        "modified_utc": modified,
    }

    title = f"ORDL DOC [{file_sha[:12]}] {rel_path}"

    if extension == PDF_EXTENSION:
        text, pdf_meta = extract_pdf_text(path)
        metadata = {**base_metadata, **pdf_meta}
        content = text if text.strip() else f"PDF document: {rel_path}"
        return LocalDocRecord(title=title, item_type="ordl_doc_pdf", content=content, metadata=metadata)

    if extension in TEXT_EXTENSIONS or extension == "":
        text, encoding = read_text_bytes(raw)
        metadata = {**base_metadata, "encoding": encoding, "line_count": text.count("\n") + 1 if text else 0}
        content = text if text else f"Text document: {rel_path}"
        return LocalDocRecord(title=title, item_type="ordl_doc_text", content=content, metadata=metadata)

    if extension in IMAGE_EXTENSIONS:
        img_meta = extract_image_metadata(path)
        metadata = {**base_metadata, **img_meta}
        content = (
            f"Image file: {rel_path}\n"
            f"SHA256: {file_sha}\n"
            f"Size: {len(raw)} bytes\n"
            f"Metadata: {json.dumps(img_meta, ensure_ascii=True)}"
        )
        return LocalDocRecord(title=title, item_type="ordl_doc_image", content=content, metadata=metadata)

    content = (
        f"Binary file: {rel_path}\n"
        f"SHA256: {file_sha}\n"
        f"Size: {len(raw)} bytes\n"
        f"Extension: {extension or '[none]'}"
    )
    return LocalDocRecord(title=title, item_type="ordl_doc_binary", content=content, metadata=base_metadata)


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, _, filenames in os.walk(root):
        base = Path(dirpath)
        for filename in filenames:
            yield base / filename


def parse_arxiv_entry(entry: ET.Element, ns: Dict[str, str]) -> Optional[ArxivRecord]:
    identifier = (entry.findtext("atom:id", default="", namespaces=ns) or "").strip()
    if not identifier:
        return None
    arxiv_id = identifier.rsplit("/", 1)[-1]
    title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
    summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
    published = (entry.findtext("atom:published", default="", namespaces=ns) or "").strip()
    updated = (entry.findtext("atom:updated", default="", namespaces=ns) or "").strip()

    authors: List[str] = []
    for author in entry.findall("atom:author", ns):
        name = (author.findtext("atom:name", default="", namespaces=ns) or "").strip()
        if name:
            authors.append(name)

    categories: List[str] = []
    for cat in entry.findall("atom:category", ns):
        term = (cat.get("term") or "").strip()
        if term:
            categories.append(term)

    links: List[str] = []
    for link in entry.findall("atom:link", ns):
        href = (link.get("href") or "").strip()
        if href:
            links.append(href)

    pdf_url = next((url for url in links if "pdf" in url), None)
    canonical_title = f"arXiv:{arxiv_id}"
    content_lines = [
        f"Title: {title}",
        f"arXiv ID: {arxiv_id}",
        f"Published: {published}",
        f"Updated: {updated}",
        "",
        "Authors:",
        ", ".join(authors) if authors else "unknown",
        "",
        "Categories:",
        ", ".join(categories) if categories else "unknown",
        "",
        "Abstract:",
        summary,
    ]
    metadata = {
        "arxiv_id": arxiv_id,
        "title": title,
        "summary": summary,
        "published_utc": published,
        "updated_utc": updated,
        "authors": authors,
        "categories": categories,
        "links": links,
        "pdf_url": pdf_url,
    }
    return ArxivRecord(title=canonical_title, content="\n".join(content_lines), metadata=metadata)


def _download_url(url: str) -> Tuple[bytes, Optional[str]]:
    try:
        with urllib.request.urlopen(url, timeout=120) as response:
            return response.read(), None
    except Exception as first_error:
        certifi_error = first_error
        try:
            import certifi  # type: ignore

            context = ssl.create_default_context(cafile=certifi.where())
            with urllib.request.urlopen(url, timeout=120, context=context) as response:
                return response.read(), None
        except Exception as second_error:
            certifi_error = second_error

        insecure_context = ssl._create_unverified_context()
        with urllib.request.urlopen(url, timeout=120, context=insecure_context) as response:
            payload = response.read()
        warning = (
            "TLS verification bypassed for this request due to local certificate-chain "
            f"validation failure: {certifi_error}"
        )
        return payload, warning


def fetch_arxiv_page(start: int, max_results: int, query: str) -> Tuple[List[ArxivRecord], Optional[str]]:
    params = {
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }
    url = f"{ARXIV_API_URL}?{urllib.parse.urlencode(params)}"
    xml_payload, warning = _download_url(url)

    root = ET.fromstring(xml_payload)
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    records: List[ArxivRecord] = []
    for entry in root.findall("atom:entry", ns):
        parsed = parse_arxiv_entry(entry, ns)
        if parsed is not None:
            records.append(parsed)
    return records, warning


def ingest_local_docs(writer: KnowledgeWriter, docs_root: Path) -> Dict[str, Any]:
    if not docs_root.exists():
        return {"error": f"Missing local docs root: {docs_root}"}

    files = sorted(iter_files(docs_root))
    existing_titles = writer.existing_titles("ordl_docs")

    ingested = 0
    skipped = 0
    failed = 0
    errors: List[Dict[str, str]] = []

    for path in files:
        try:
            record = build_local_doc_record(path, docs_root)
            if record.title in existing_titles:
                skipped += 1
                continue
            writer.insert_item(
                item_type=record.item_type,
                title=record.title,
                content=record.content,
                source="ordl_docs",
                metadata=record.metadata,
                confidence=1.0,
            )
            existing_titles.add(record.title)
            ingested += 1
        except Exception as exc:
            failed += 1
            errors.append({"path": str(path), "error": str(exc)})

    return {
        "source": "ordl_docs",
        "root": str(docs_root),
        "total_files_seen": len(files),
        "ingested": ingested,
        "skipped_existing": skipped,
        "failed": failed,
        "errors": errors,
    }


def ingest_arxiv(
    writer: KnowledgeWriter,
    days: int,
    query: str,
    window_days: int,
    page_size: int,
    max_records: int,
    start_offset: int = 0,
) -> Dict[str, Any]:
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=days)
    existing_titles = writer.existing_titles("arxiv")

    requests = 0
    scanned = 0
    ingested = 0
    skipped = 0
    failed = 0
    errors: List[Dict[str, str]] = []
    warnings: List[str] = []
    stop = False

    query_windows: List[Tuple[str, int]] = []
    if window_days > 0:
        cursor = cutoff
        while cursor < now:
            end = min(cursor + timedelta(days=window_days), now)
            date_clause = f"submittedDate:[{format_arxiv_datetime(cursor)} TO {format_arxiv_datetime(end)}]"
            window_query = f"({query}) AND {date_clause}"
            query_windows.append((window_query, 0))
            cursor = end
    else:
        query_windows.append((query, max(start_offset, 0)))

    for window_query, initial_start in query_windows:
        start = initial_start
        while not stop and scanned < max_records:
            requests += 1
            try:
                page, warning = fetch_arxiv_page(start, page_size, window_query)
                if warning:
                    warnings.append(warning)
            except Exception as exc:
                errors.append({"request_start": str(start), "error": str(exc), "query": window_query})
                break

            if not page:
                break

            start += len(page)
            for record in page:
                scanned += 1
                if scanned > max_records:
                    stop = True
                    break

                if record.title in existing_titles:
                    skipped += 1
                    continue

                try:
                    writer.insert_item(
                        item_type="ai_research",
                        title=record.title,
                        content=record.content,
                        source="arxiv",
                        metadata=record.metadata,
                        confidence=1.0,
                    )
                    existing_titles.add(record.title)
                    ingested += 1
                except Exception as exc:
                    failed += 1
                    errors.append({"title": record.title, "error": str(exc), "query": window_query})

            # arXiv recommends modest polling intervals.
            time.sleep(1.5)

    return {
        "source": "arxiv",
        "query": query,
        "window_days": window_days,
        "start_offset": start_offset,
        "cutoff_utc": cutoff.isoformat(),
        "requests": requests,
        "records_scanned": scanned,
        "ingested": ingested,
        "skipped_existing": skipped,
        "failed": failed,
        "warnings": warnings,
        "errors": errors,
    }


def write_report(report_dir: Path, report: Dict[str, Any]) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    report_path = report_dir / f"ingestion_report_{stamp}.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report_path


def main() -> int:
    args = parse_args()

    db_path = Path(args.db_path)
    docs_root = Path(args.local_docs_root)
    report: Dict[str, Any] = {"started_utc": datetime.now(timezone.utc).isoformat()}

    with KnowledgeWriter(db_path) as writer:
        if not args.skip_local_docs:
            report["local_docs"] = ingest_local_docs(writer, docs_root)
        if not args.skip_arxiv:
            report["arxiv"] = ingest_arxiv(
                writer=writer,
                days=args.arxiv_days,
                query=args.arxiv_query,
                window_days=args.arxiv_window_days,
                page_size=args.arxiv_page_size,
                max_records=args.arxiv_max_records,
                start_offset=args.arxiv_start,
            )

    report["completed_utc"] = datetime.now(timezone.utc).isoformat()
    report["db_path"] = str(db_path)
    report_path = write_report(Path(args.report_dir), report)

    print(json.dumps(report, indent=2))
    print(f"Report written: {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
