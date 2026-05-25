"""Collections API client for the get_consumer_documents MCP tool."""

from .mcp.tool.document_client import DocumentFetchResult, fetch_case_documents

__all__ = ["DocumentFetchResult", "fetch_case_documents"]
