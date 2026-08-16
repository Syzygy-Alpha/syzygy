from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SYZYGY_OBSERVATORY_",
        extra="ignore",
    )

    env: str = Field(default="development")
    service_name: str = Field(default="syzygy-observatory")
    version: str = Field(default="0.1.0")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8020)
    database_url: str = Field(default="sqlite:///./data/observatory.db")
    foundation_url: str = Field(default="http://127.0.0.1:8000")
    register_with_foundation: bool = Field(default=False)
    foundation_username: str = Field(default="admin")
    foundation_password: SecretStr = Field(default=SecretStr("change-me"))
    foundation_module_polling_enabled: bool = Field(default=False)
    foundation_module_polling_interval_seconds: int = Field(default=60, ge=1)
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
