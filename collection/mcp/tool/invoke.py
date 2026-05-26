"""Shared get_consumer_documents invocation for Lambda and AgentCore Runtime."""

from __future__ import annotations

import logging
from typing import Any

from .api_key import resolve_ri_core_api_key
from .document_client import fetch_case_documents

logger = logging.getLogger(__name__)


def _field(payload: dict[str, Any], *keys: str) -> str:
    for key in keys:
        val = payload.get(key)
        if val is not None and str(val).strip():
            return str(val).strip()
    return ""


def invoke_get_consumer_documents(payload: dict[str, Any]) -> dict[str, Any]:
    """Execute the tool; returns a JSON-serializable result dict."""
    case_id = _field(payload, "case_id", "caseId")
    account_id = _field(payload, "account_id", "accountId")
    collection_core_base_api_url = _field(
        payload, "collection_core_base_api_url", "collectionCoreBaseApiUrl"
    )
    timeout_raw = payload.get("timeout_s") if payload.get("timeout_s") is not None else payload.get("timeoutS")
    timeout_s = float(timeout_raw) if timeout_raw is not None else None

    api_key = resolve_ri_core_api_key()
    if not api_key:
        return {
            "storage_urls": [],
            "api_response_status": "ERROR",
            "ok": False,
            "http_status": None,
            "error_message": (
                "RI API key not configured. Set RI_CORE_API_KEY (local dev), "
                "RI_CORE_API_KEY_SECRET_ARN (from agentcore add credential --type api-key), "
                "or COLLECTION_CORE_DOCUMENTS_API_SSM_PARAMETER."
            ),
        }

    logger.info("get_consumer_documents case_id=%s", case_id)
    return fetch_case_documents(
        case_id,
        account_id,
        collection_core_base_api_url,
        timeout_s=timeout_s,
        api_key=api_key,
    ).to_dict()
