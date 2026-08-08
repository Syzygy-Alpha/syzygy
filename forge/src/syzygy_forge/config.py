from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SYZYGY_FORGE_",
        extra="ignore",
    )

    env: str = Field(default="development")
    service_name: str = Field(default="syzygy-forge")
    version: str = Field(default="0.1.0")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8010)
    foundation_url: str = Field(default="http://127.0.0.1:8000")
    register_with_foundation: bool = Field(default=False)
    foundation_username: str = Field(default="admin")
    foundation_password: SecretStr = Field(default=SecretStr("change-me"))
    workspace_root: Path = Field(default=Path("."))
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
