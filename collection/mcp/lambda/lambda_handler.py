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

from collection.mcp.tool.invoke import invoke_get_consumer_documents

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    logger.info(
        "get_consumer_documents aws_request_id=%s",
        getattr(context, "aws_request_id", None),
    )
    body = invoke_get_consumer_documents(event if isinstance(event, dict) else {})
    return {"statusCode": 200, "body": json.dumps(body)}
