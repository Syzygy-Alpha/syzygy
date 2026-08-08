from functools import lru_cache

from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="SYZYGY_",
        extra="ignore",
    )

    env: str = Field(default="development")
    service_name: str = Field(default="syzygy-foundation")
    version: str = Field(default="0.1.0")
    host: str = Field(default="127.0.0.1")
    port: int = Field(default=8000)
    database_url: str = Field(default="sqlite:///./data/foundation.db")
    nats_url: str = Field(default="nats://localhost:4222")
    nats_enabled: bool = Field(default=True)
    jwt_secret: SecretStr = Field(default=SecretStr("development-only-change-me"))
    jwt_algorithm: str = Field(default="HS256")
    jwt_expires_minutes: int = Field(default=60)
    admin_username: str = Field(default="admin")
    admin_password: SecretStr = Field(default=SecretStr("change-me"))
    log_level: str = Field(default="INFO")

    @model_validator(mode="after")
    def require_non_default_secrets_outside_development(self) -> "Settings":
        protected_envs = {"production", "staging"}
        if self.env in protected_envs:
            default_secret = self.jwt_secret.get_secret_value() == "development-only-change-me"
            default_password = self.admin_password.get_secret_value() == "change-me"
            if default_secret or default_password:
                msg = "production-like environments require explicit JWT secret and admin password"
                raise ValueError(msg)
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()

