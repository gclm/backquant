from __future__ import annotations

import json
import os
import time
import urllib.request
from datetime import datetime
from pathlib import Path

from flask import Blueprint, current_app, jsonify

bp_system = Blueprint("bp_system", __name__, url_prefix="/api/system")


_BUNDLE_REQUIRED_FILES = ("future_info.json", "instruments.pk", "trading_dates.npy")
_BUNDLE_META_CACHE: dict[str, float | int | str | None] = {"total_bytes": None, "url": None, "expires_at": 0.0}
_BUNDLE_META_TTL_SECONDS = 10 * 60


def _bundle_is_ready(bundle_path: Path) -> bool:
    if not bundle_path.exists() or not bundle_path.is_dir():
        return False
    try:
        if not any(bundle_path.iterdir()):
            return False
    except OSError:
        return False
    for filename in _BUNDLE_REQUIRED_FILES:
        candidate = bundle_path / filename
        try:
            if not candidate.is_file() or candidate.stat().st_size <= 0:
                return False
        except OSError:
            return False
    return True


def _dir_size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        try:
            return path.stat().st_size
        except OSError:
            return 0
    total = 0
    for root, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += (Path(root) / name).stat().st_size
            except OSError:
                continue
    return total


def _bundle_status_file() -> Path:
    raw = os.environ.get("RQALPHA_BUNDLE_STATUS_FILE", "").strip()
    if raw:
        return Path(raw).expanduser()
    return Path("/data/rqalpha/bundle_status.json")


def _read_bundle_status() -> dict | None:
    path = _bundle_status_file()
    if not path.exists():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    return payload


def _bundle_total_bytes(status_payload: dict | None) -> int | None:
    raw = os.environ.get("RQALPHA_BUNDLE_TOTAL_BYTES", "").strip()
    if raw:
        try:
            value = int(raw)
        except ValueError:
            value = None
        if value and value > 0:
            return value

    if isinstance(status_payload, dict):
        raw_status = status_payload.get("total_bytes")
        try:
            value = int(raw_status)
        except (TypeError, ValueError):
            value = None
        if value and value > 0:
            return value

    return _bundle_total_bytes_from_head(status_payload)


def _bundle_url_candidates(status_payload: dict | None) -> list[str]:
    explicit = os.environ.get("RQALPHA_BUNDLE_URL", "").strip()
    if explicit:
        return [explicit]
    if isinstance(status_payload, dict):
        url = str(status_payload.get("url") or "").strip()
        if url:
            return [url]

    base = os.environ.get(
        "RQALPHA_BUNDLE_URL_BASE",
        "http://bundle.assets.ricequant.com/bundles_v4",
    ).strip()
    if not base:
        return []

    candidates: list[str] = []
    now = datetime.utcnow()
    year = now.year
    month = now.month
    for _ in range(0, 12):
        candidates.append(f"{base}/rqbundle_{year}{month:02d}.tar.bz2")
        month -= 1
        if month <= 0:
            month = 12
            year -= 1
    return candidates


def _bundle_total_bytes_from_head(status_payload: dict | None) -> int | None:
    now = time.time()
    if _BUNDLE_META_CACHE["expires_at"] and now < float(_BUNDLE_META_CACHE["expires_at"]):
        cached = _BUNDLE_META_CACHE.get("total_bytes")
        return int(cached) if isinstance(cached, (int, float)) and cached > 0 else None

    candidates = _bundle_url_candidates(status_payload)
    if not candidates:
        return None

    total = None
    resolved_url = None
    for url in candidates:
        try:
            request = urllib.request.Request(url, method="HEAD")
            with urllib.request.urlopen(request, timeout=5) as response:
                length = response.headers.get("Content-Length")
            if length:
                total = int(length)
                resolved_url = url
                break
        except Exception:
            continue

    _BUNDLE_META_CACHE["total_bytes"] = total
    _BUNDLE_META_CACHE["url"] = resolved_url
    _BUNDLE_META_CACHE["expires_at"] = now + _BUNDLE_META_TTL_SECONDS
    return total if total and total > 0 else None


@bp_system.get("/bundle-status")
def bundle_status():
    bundle_path = Path(current_app.config["RQALPHA_BUNDLE_PATH"]).expanduser()
    ready = _bundle_is_ready(bundle_path)
    status_payload = _read_bundle_status()
    status = None
    message = None
    work_dir = None
    if isinstance(status_payload, dict):
        status = str(status_payload.get("status") or "").strip() or None
        message = str(status_payload.get("message") or "").strip() or None
        work_dir = str(status_payload.get("work_dir") or "").strip() or None

    if ready:
        status = "ready"
        message = "bundle ready"
        size_path = bundle_path
    else:
        size_path = Path(work_dir) if work_dir else bundle_path
        if not size_path.exists():
            size_path = bundle_path

    downloaded_bytes = _dir_size_bytes(size_path)
    if (status or "").lower() == "downloading" and downloaded_bytes <= 0:
        # rqalpha may download to a temp file in /tmp before extracting to bundle dir.
        temp_bundle = Path("/tmp/rq.bundle")
        if temp_bundle.exists():
            downloaded_bytes = _dir_size_bytes(temp_bundle)
    total_bytes = _bundle_total_bytes(status_payload)

    progress: dict[str, float | int] = {"downloaded_bytes": downloaded_bytes}
    if total_bytes:
        progress["total_bytes"] = total_bytes
        if downloaded_bytes > 0:
            percent = min(downloaded_bytes / total_bytes * 100.0, 100.0)
            progress["percent"] = round(percent, 2)

    payload = {
        "status": status or ("ready" if ready else "downloading"),
        "message": message or ("bundle ready" if ready else "bundle downloading"),
        "progress": progress,
    }
    return jsonify(payload)
