from pathlib import Path

from syzygy_nerv.catalog import SurfaceCatalog
from syzygy_nerv.config import Settings


def test_surface_catalog_lists_known_modules(tmp_path: Path) -> None:
    settings = Settings(workspace_root=tmp_path, python_executable="python")
    catalog = SurfaceCatalog(settings)

    names = [entry.name for entry in catalog.list()]

    assert names == ["foundation", "forge", "observatory", "mycelium", "nerv"]
    assert catalog.get("nerv") is not None
    assert catalog.get("nerv").launch_enabled is False
    assert catalog.get("forge").launch_command[:3] == ["python", "-m", "uvicorn"]
