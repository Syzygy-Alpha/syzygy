from syzygy_mycelium.config import Settings


def test_default_settings() -> None:
    settings = Settings()

    assert settings.service_name == "syzygy-mycelium"
    assert settings.port == 8030
    assert settings.node_id == "local-node"
    assert settings.node_name == "local"
    assert settings.register_with_foundation is False
