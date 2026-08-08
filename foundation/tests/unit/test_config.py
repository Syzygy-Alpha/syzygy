import pytest

from syzygy_foundation.config import Settings


def test_development_settings_allow_local_defaults() -> None:
    settings = Settings(nats_enabled=False)

    assert settings.service_name == "syzygy-foundation"
    assert settings.version == "0.1.0"


def test_production_rejects_default_secrets() -> None:
    with pytest.raises(ValueError, match="production-like environments"):
        Settings(env="production")

