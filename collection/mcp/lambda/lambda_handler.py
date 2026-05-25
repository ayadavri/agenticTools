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

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)
from collection.mcp.tool.document_client import fetch_case_documents

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    case_id = (event.get("case_id") or event.get("caseId") or "").strip()
    account_id = (event.get("account_id") or event.get("accountId") or "").strip()
    collection_core_base_api_url = (event.get("collection_core_base_api_url") or event.get("collectionCoreBaseApiUrl") or "").strip()
    logger.info(
        "get_consumer_documents case_id=%s aws_request_id=%s",
        case_id,
        getattr(context, "aws_request_id", None),
    )

    result = fetch_case_documents(case_id, account_id, collection_core_base_api_url)
    return {"statusCode": 200, "body": json.dumps(result.to_dict())}
