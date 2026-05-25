"""Fetch case document storage URLs from the Resident Interface collections API."""

from __future__ import annotations

import json
import logging
import ssl
import time
from dataclasses import asdict, dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)
_DOCUMENTS_PATH = "/collections/v1/cases/{case_id}/documents?enable_signed_url=true"


@dataclass(frozen=True)
class DocumentFetchResult:
    storage_urls: list[str]
    api_response_status: str  # SUCCESS | ERROR | HUMAN_REVIEW
    ok: bool
    http_status: int | None
    error_message: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_storage_url(raw: Any) -> str:
    if raw is None:
        return ""
    if isinstance(raw, str):
        return raw.strip()
    return str(raw).strip() if raw else ""


def extract_storage_urls(data: Any) -> list[str]:
    if not isinstance(data, dict):
        return []

    direct = _normalize_storage_url(data.get("storageUrl"))
    if direct:
        return [direct]

    items = data.get("items")
    if not isinstance(items, list):
        return []

    urls = []
    for entry in items:
        if isinstance(entry, dict):
            url = _normalize_storage_url(entry.get("storageUrl"))
            if url:
                urls.append(url)
    return urls


def fetch_case_documents(
    case_id: str,
    account_id: str,
    collection_core_base_api_url: str,
    timeout_s: float | None = None,
) -> DocumentFetchResult:
    """GET case documents and return signed storage URLs."""
    cid = (case_id or "").strip()
    aid = (account_id or "").strip()

    if not cid:
        return DocumentFetchResult([], "ERROR", False, None, "case_id is required")
    if not aid:
        return DocumentFetchResult([], "ERROR", False, None, "account_id is required")

    base = (collection_core_base_api_url).rstrip("/")
    url = f"{base}{_DOCUMENTS_PATH.format(case_id=cid)}"
    headers = {"content-type": "application/json", "x-account-id": aid}
    token = None
    if token:
        headers["x-api-key"] = token

    timeout = timeout_s if timeout_s is not None else float(timeout_s or 30.0)
    req = Request(url, method="GET", headers=headers)
    started = time.monotonic()
    status: int | None = None
    raw_body = b""

    try:
        with urlopen(req, timeout=timeout, context=ssl.create_default_context()) as resp:  # noqa: S310
            status = getattr(resp, "status", None) or resp.getcode()
            raw_body = resp.read()
        logger.info(
            "Documents API ok case_id=%s status=%s elapsed_ms=%.0f",
            cid,
            status,
            (time.monotonic() - started) * 1000,
        )
    except HTTPError as e:
        return DocumentFetchResult(
            [],
            "ERROR",
            False,
            int(e.code),
            str(e.reason) if e.reason else f"HTTP {e.code}",
        )
    except (URLError, TimeoutError, OSError) as e:
        msg = getattr(e, "reason", None) or str(e)
        return DocumentFetchResult([], "ERROR", False, None, str(msg))

    if status is not None and int(status) >= 400:
        return DocumentFetchResult([], "ERROR", False, int(status), f"HTTP {status}")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return DocumentFetchResult([], "ERROR", False, int(status) if status else None, "invalid JSON")

    if not isinstance(payload, dict) or payload.get("count", 0) <= 0:
        return DocumentFetchResult(
            [],
            "HUMAN_REVIEW",
            True,
            int(status) if status else None,
            "no documents found for case",
        )

    storage_urls = extract_storage_urls(payload)
    if not storage_urls:
        return DocumentFetchResult(
            [],
            "HUMAN_REVIEW",
            True,
            int(status) if status else None,
            "documents returned but no storage URLs",
        )

    return DocumentFetchResult(storage_urls, "SUCCESS", True, int(status) if status else None, None)
