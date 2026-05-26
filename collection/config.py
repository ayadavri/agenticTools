from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    aws_region: str = "us-east-1"
    ri_core_api_key: str = ""
    ri_core_api_key_secret_arn: str = ""
    collection_core_documents_api_ssm_parameter: str = "/agents/COLLECTION_CORE_DOCUMENTS_API_KEY"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
