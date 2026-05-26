"""Resolve RI Core API key for outbound HTTP calls.

Lambda gateway targets only receive IAM invoke from AgentCore Gateway; Gateway does
not inject API-key outbound auth for Lambda (see AWS outbound-auth matrix). Store the
key with AgentCore Identity (``agentcore add credential --type api-key``) and point
the Lambda at the returned Secrets Manager ARN, or use SSM / a direct env var.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache

from collection.config import get_settings

logger = logging.getLogger(__name__)


def _parse_secret_string(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    if not isinstance(payload, dict):
        return text
    for key in ("apiKey", "api_key", "API_KEY", "value", "secret"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return text


@lru_cache(maxsize=1)
def resolve_ri_core_api_key() -> str | None:
    """Load API key once per execution environment (cached)."""
    settings = get_settings()

    if settings.ri_core_api_key.strip():
        return settings.ri_core_api_key.strip()

    secret_arn = settings.ri_core_api_key_secret_arn.strip()
    if secret_arn:
        key = _load_secrets_manager(secret_arn)
        if key:
            return key
        logger.warning("Secrets Manager returned empty key for %s", secret_arn)

    param = settings.collection_core_documents_api_ssm_parameter.strip()
    if param:
        key = _load_ssm(param, settings.aws_region.strip() or "us-east-1")
        if key:
            return key
        logger.warning("SSM parameter empty or missing: %s", param)

    return None


def _load_secrets_manager(secret_arn: str) -> str | None:
    try:
        import boto3
    except ImportError:
        logger.warning("boto3 not available; cannot read Secrets Manager")
        return None

    try:
        client = boto3.client("secretsmanager")
        resp = client.get_secret_value(SecretId=secret_arn)
    except Exception as exc:
        logger.warning("Secrets Manager read failed (%s): %s", secret_arn, exc)
        return None

    raw = resp.get("SecretString") or ""
    if not raw and resp.get("SecretBinary"):
        raw = resp["SecretBinary"].decode("utf-8", errors="replace")
    parsed = _parse_secret_string(raw)
    return parsed or None


def _load_ssm(name: str, region: str) -> str | None:
    try:
        import boto3
    except ImportError:
        logger.warning("boto3 not available; cannot read SSM")
        return None

    try:
        client = boto3.client("ssm", region_name=region)
        resp = client.get_parameter(Name=name, WithDecryption=True)
    except Exception as exc:
        logger.warning("SSM read failed (%s): %s", name, exc)
        return None

    value = resp.get("Parameter", {}).get("Value")
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
