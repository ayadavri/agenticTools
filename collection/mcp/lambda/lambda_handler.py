"""
MCP tool worker: get_consumer_documents

AgentCore Gateway calls this Lambda after MCP tools/call on the gateway /mcp endpoint.
"""

from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any

# Zip layout: /var/task/collection/... — repo root must be on sys.path.
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from collection.mcp.tool.api_key import resolve_ri_core_api_key
from collection.mcp.tool.document_client import fetch_case_documents

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    case_id = (event.get("case_id") or event.get("caseId") or "").strip()
    account_id = (event.get("account_id") or event.get("accountId") or "").strip()
    collection_core_base_api_url = (event.get("collection_core_base_api_url") or event.get("collectionCoreBaseApiUrl") or "").strip()
    timeout_raw = event.get("timeout_s") or event.get("timeoutS")
    timeout_s = float(timeout_raw) if timeout_raw is not None else None

    api_key = resolve_ri_core_api_key()
    if not api_key:
        body = {
            "storage_urls": [],
            "api_response_status": "ERROR",
            "ok": False,
            "http_status": None,
            "error_message": (
                "RI API key not configured. Set RI_CORE_API_KEY, RI_CORE_API_KEY_SECRET_ARN "
                "(from agentcore add credential --type api-key), or COLLECTION_CORE_DOCUMENTS_API_SSM_PARAMETER."
            ),
        }
        return {"statusCode": 200, "body": json.dumps(body)}

    logger.info(
        "get_consumer_documents case_id=%s aws_request_id=%s",
        case_id,
        getattr(context, "aws_request_id", None),
    )

    result = fetch_case_documents(
        case_id,
        account_id,
        collection_core_base_api_url,
        timeout_s=timeout_s,
        api_key=api_key,
    )
    return {"statusCode": 200, "body": json.dumps(result.to_dict())}
