from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SYZYGY_MYCELIUM_",
        extra="ignore",
    )

    env: str = Field(default="development")
    service_name: str = Field(default="syzygy-mycelium")
    version: str = Field(default="0.1.0")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8030)
    node_id: str = Field(default="local-node", min_length=1)
    node_name: str = Field(default="local", min_length=1)
    register_with_foundation: bool = Field(default=False)
    foundation_url: str = Field(default="http://127.0.0.1:8000")
    foundation_username: str = Field(default="admin")
    foundation_password: SecretStr = Field(default=SecretStr("change-me"))
    log_level: str = Field(default="INFO")


@lru_cache
def get_settings() -> Settings:
    return Settings()
