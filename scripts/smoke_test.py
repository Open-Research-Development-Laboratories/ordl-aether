#!/usr/bin/env python3
"""
End-to-end smoke test for AETHER.

Usage:
  python scripts/smoke_test.py
  python scripts/smoke_test.py --skip-image
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import sys
import time
import urllib.error
import urllib.request
from typing import Dict, Tuple

try:
    from PIL import Image
except Exception:  # pragma: no cover - fallback path
    Image = None


FALLBACK_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADUlEQVQImWNgYGD4DwABBAEAQ1vY4QAAAABJRU5ErkJggg=="
)


def make_smoke_image_bytes() -> bytes:
    if Image is None:
        return FALLBACK_PNG
    buffer = io.BytesIO()
    img = Image.new("RGB", (32, 32), color=(23, 120, 210))
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def http_json(method: str, url: str, payload: Dict | None = None, timeout: int = 45) -> Tuple[int, Dict]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url=url, data=data, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        return resp.status, json.loads(body)


def http_status(url: str, timeout: int = 20) -> int:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.status


def multipart_image_post(url: str, analysis_type: str, timeout: int = 180) -> Tuple[int, Dict]:
    boundary = "----AETHERBoundary7MA4YWxkTrZu0gW"
    CRLF = "\r\n"
    parts = []
    parts.append(f"--{boundary}{CRLF}".encode())
    parts.append(
        (
            f'Content-Disposition: form-data; name="analysis_type"{CRLF}{CRLF}'
            f"{analysis_type}{CRLF}"
        ).encode()
    )
    parts.append(f"--{boundary}{CRLF}".encode())
    parts.append(
        (
            f'Content-Disposition: form-data; name="file"; filename="smoke.png"{CRLF}'
            f"Content-Type: image/png{CRLF}{CRLF}"
        ).encode()
    )
    parts.append(make_smoke_image_bytes())
    parts.append(CRLF.encode())
    parts.append(f"--{boundary}--{CRLF}".encode())
    body = b"".join(parts)

    req = urllib.request.Request(
        url=url,
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        response_body = resp.read().decode("utf-8", errors="replace")
        return resp.status, json.loads(response_body)


def assert_ok(condition: bool, message: str):
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AETHER smoke tests.")
    parser.add_argument("--frontend-url", default="http://localhost:3000", help="Frontend URL")
    parser.add_argument("--backend-url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--skip-image", action="store_true", help="Skip image analyze endpoint")
    args = parser.parse_args()

    started = time.perf_counter()
    print("Running smoke tests...")

    try:
        frontend_status = http_status(args.frontend_url)
        assert_ok(frontend_status == 200, f"Frontend not healthy (status={frontend_status})")
        print("  [ok] frontend reachable")

        health_status, health = http_json("GET", f"{args.backend_url}/health")
        assert_ok(health_status == 200, f"Health endpoint failed ({health_status})")
        assert_ok(health.get("status") in {"healthy", "degraded"}, "Unexpected health payload")
        print("  [ok] backend health endpoint")

        text_status, text_resp = http_json(
            "POST",
            f"{args.backend_url}/api/v1/analyze/text",
            payload={
                "data_type": "text",
                "content": "AETHER smoke test for NLP pipeline validation.",
                "context": {"tasks": ["sentiment"]},
            },
            timeout=90,
        )
        assert_ok(text_status == 200, f"Text analyze failed ({text_status})")
        assert_ok(text_resp.get("success") is True, "Text analyze success=false")
        print("  [ok] text analyze")

        anomaly_status, anomaly_resp = http_json(
            "POST",
            f"{args.backend_url}/api/v1/analyze/anomalies",
            payload={
                "data_type": "time_series",
                "content": "1,2,3,2,3,2,1,50,2,3,2",
                "context": {"method": "ensemble", "sensitivity": "medium"},
            },
            timeout=90,
        )
        assert_ok(anomaly_status == 200, f"Anomaly analyze failed ({anomaly_status})")
        assert_ok(anomaly_resp.get("success") is True, "Anomaly analyze success=false")
        print("  [ok] anomaly analyze")

        if not args.skip_image:
            image_status, image_resp = multipart_image_post(
                f"{args.backend_url}/api/v1/analyze/image",
                analysis_type="classification",
                timeout=300,
            )
            assert_ok(image_status == 200, f"Image analyze failed ({image_status})")
            assert_ok(image_resp.get("success") is True, "Image analyze success=false")
            print("  [ok] image analyze")
        else:
            print("  [skip] image analyze")

    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        print(f"SMOKE FAILED: HTTP {exc.code} -> {body}")
        return 1
    except Exception as exc:
        print(f"SMOKE FAILED: {exc}")
        return 1

    elapsed = time.perf_counter() - started
    print(f"Smoke tests passed in {elapsed:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
