from pathlib import Path

from syzygy_nerv.config import Settings


def test_default_settings() -> None:
    settings = Settings()

    assert settings.service_name == "syzygy-nerv"
    assert settings.port == 8040
    assert settings.foundation_registry_enabled is False
    assert settings.python_executable == "python"
    assert isinstance(settings.workspace_root, Path)
