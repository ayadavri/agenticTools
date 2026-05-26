"""
AgentCore Runtime entrypoint for get_consumer_documents.

Exposes POST /invocations and GET /ping on port 8080 (BedrockAgentCoreApp contract).
"""

from __future__ import annotations

import logging
import os
import sys

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from bedrock_agentcore import BedrockAgentCoreApp

from collection.mcp.tool.invoke import invoke_get_consumer_documents

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = BedrockAgentCoreApp()


@app.entrypoint
def invoke(payload: dict) -> dict:
    """Handle Runtime invocation payload (same fields as MCP tool / Lambda event)."""
    if not isinstance(payload, dict):
        payload = {}
    return invoke_get_consumer_documents(payload)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    logger.info("Starting AgentCore Runtime on port %s", port)
    app.run(port=port)
