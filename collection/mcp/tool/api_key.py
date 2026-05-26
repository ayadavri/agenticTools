"""Resolve RI Core API key from SSM Parameter Store."""

from __future__ import annotations

import logging
from functools import lru_cache

from collection.config import get_settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def resolve_ri_core_api_key() -> str | None:
    """Load API key once per execution environment (cached)."""
    settings = get_settings()

    param = settings.collection_core_documents_api_ssm_parameter.strip()
    if not param:
        return None

    key = _load_ssm(param, settings.aws_region.strip() or "us-east-1")
    if key:
        return key

    logger.warning("SSM parameter empty or missing: %s", param)
    return None


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
