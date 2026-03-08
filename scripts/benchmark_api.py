#!/usr/bin/env python3
"""
Simple API benchmark for AETHER endpoints.

Usage:
  python scripts/benchmark_api.py --requests 40 --concurrency 8
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import statistics
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List


@dataclass
class Sample:
    ok: bool
    latency_ms: float
    status: int
    error: str = ""


def post_json(url: str, payload: Dict, timeout: int = 120) -> Sample:
    started = time.perf_counter()
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw)
            ok = bool(parsed.get("success", True)) and resp.status == 200
            return Sample(ok=ok, latency_ms=(time.perf_counter() - started) * 1000, status=resp.status)
    except urllib.error.HTTPError as exc:
        return Sample(
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            status=exc.code,
            error=exc.read().decode("utf-8", errors="replace")[:200],
        )
    except Exception as exc:
        return Sample(
            ok=False,
            latency_ms=(time.perf_counter() - started) * 1000,
            status=0,
            error=str(exc)[:200],
        )


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    idx = min(len(sorted_values) - 1, max(0, int(round((p / 100.0) * (len(sorted_values) - 1)))))
    return sorted_values[idx]


def run_benchmark(request_count: int, concurrency: int, call: Callable[[], Sample]) -> Dict:
    samples: List[Sample] = []
    started = time.perf_counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrency) as pool:
        futures = [pool.submit(call) for _ in range(request_count)]
        for fut in concurrent.futures.as_completed(futures):
            samples.append(fut.result())

    elapsed = time.perf_counter() - started
    latencies = [s.latency_ms for s in samples]
    ok_count = sum(1 for s in samples if s.ok)

    return {
        "total_requests": request_count,
        "success_count": ok_count,
        "error_count": request_count - ok_count,
        "success_rate": round(ok_count / request_count, 4),
        "duration_seconds": round(elapsed, 3),
        "throughput_rps": round(request_count / elapsed, 3) if elapsed > 0 else 0.0,
        "latency_ms": {
            "min": round(min(latencies), 2) if latencies else 0.0,
            "avg": round(statistics.mean(latencies), 2) if latencies else 0.0,
            "p50": round(percentile(latencies, 50), 2),
            "p95": round(percentile(latencies, 95), 2),
            "p99": round(percentile(latencies, 99), 2),
            "max": round(max(latencies), 2) if latencies else 0.0,
        },
        "sample_errors": [s.error for s in samples if (not s.ok and s.error)][:5],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark AETHER API endpoints.")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--requests", type=int, default=40, help="Requests per endpoint")
    parser.add_argument("--concurrency", type=int, default=8, help="Concurrent workers")
    parser.add_argument(
        "--endpoints",
        default="text,anomaly",
        help="Comma-separated endpoints: text,anomaly",
    )
    parser.add_argument("--output", default="", help="Optional JSON output path")
    args = parser.parse_args()

    selected = {item.strip() for item in args.endpoints.split(",") if item.strip()}
    report: Dict[str, Dict] = {}

    if "text" in selected:
        text_url = f"{args.backend_url}/api/v1/analyze/text"
        report["text"] = run_benchmark(
            args.requests,
            args.concurrency,
            lambda: post_json(
                text_url,
                {
                    "data_type": "text",
                    "content": "Benchmark payload for AETHER NLP endpoint.",
                    "context": {"tasks": ["sentiment"]},
                },
            ),
        )

    if "anomaly" in selected:
        anomaly_url = f"{args.backend_url}/api/v1/analyze/anomalies"
        report["anomaly"] = run_benchmark(
            args.requests,
            args.concurrency,
            lambda: post_json(
                anomaly_url,
                {
                    "data_type": "time_series",
                    "content": "1,2,2,3,2,1,2,2,3,2,1,50,2,3,2",
                    "context": {"method": "ensemble", "sensitivity": "medium"},
                },
            ),
        )

    rendered = json.dumps(report, indent=2)
    print(rendered)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(rendered + "\n", encoding="utf-8")
        print(f"Wrote benchmark report: {output_path}")

    failures = any(item.get("error_count", 0) > 0 for item in report.values())
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())

