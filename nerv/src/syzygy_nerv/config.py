from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


def default_workspace_root() -> Path:
    return Path(__file__).resolve().parents[3]


def default_runtime_logs_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "runtime-logs"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SYZYGY_NERV_",
        extra="ignore",
    )

    env: str = Field(default="development")
    service_name: str = Field(default="syzygy-nerv")
    version: str = Field(default="0.1.0")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8040)
    module_host: str = Field(default="127.0.0.1")
    workspace_root: Path = Field(default_factory=default_workspace_root)
    python_executable: str = Field(default="python", min_length=1)
    runtime_logs_dir: Path = Field(default_factory=default_runtime_logs_dir)
    probe_timeout_seconds: float = Field(default=0.75, ge=0.1, le=10.0)
    foundation_registry_enabled: bool = Field(default=False)
    register_with_foundation: bool = Field(default=False)
    foundation_url: str = Field(default="http://127.0.0.1:8000")
    foundation_username: str = Field(default="admin")
    foundation_password: SecretStr = Field(default=SecretStr("change-me"))
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
