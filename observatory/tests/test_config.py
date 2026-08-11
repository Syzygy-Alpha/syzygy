from syzygy_observatory.config import Settings


def test_default_settings() -> None:
    settings = Settings()

    assert settings.service_name == "syzygy-observatory"
    assert settings.port == 8020
    assert settings.database_url == "sqlite:///./data/observatory.db"
    assert settings.register_with_foundation is False
