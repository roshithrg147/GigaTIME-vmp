from functools import lru_cache
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Required — container will crash at startup if this is missing.
    gemini_api_key: str

    # Optional with sensible defaults
    gemini_model: str = "gemini-2.5-flash"
    database_url: str = "sqlite:///./gigatime_jobs.db"
    log_level: str = "INFO"
    environment: str = "production"

    # Azure / GigaTIME model settings
    gigatime_model_endpoint: str = "MOCK"
    azure_tenant_id: Optional[str] = None
    azure_client_id: Optional[str] = None
    azure_client_secret: Optional[str] = None
    azure_subscription_id: Optional[str] = None
    azure_resource_group: Optional[str] = None
    azure_workspace_name: Optional[str] = None

    # Optional HuggingFace settings
    hf_api_token: Optional[str] = None
    hf_gigatime_endpoint_url: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
