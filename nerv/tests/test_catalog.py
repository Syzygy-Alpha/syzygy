from pathlib import Path

from syzygy_nerv.catalog import SurfaceCatalog
from syzygy_nerv.config import Settings


def test_surface_catalog_lists_known_modules(tmp_path: Path) -> None:
    settings = Settings(workspace_root=tmp_path, python_executable="python")
    catalog = SurfaceCatalog(settings)

    names = [entry.name for entry in catalog.list_entries()]
    nerv = catalog.get("nerv")
    forge = catalog.get("forge")

    assert names == ["foundation", "forge", "observatory", "mycelium", "nerv"]
    assert nerv is not None
    assert forge is not None
    assert nerv.launch_enabled is False
    assert forge.launch_command[:3] == ["python", "-m", "uvicorn"]
    assert [action.name for action in forge.actions] == [
        "current-project",
        "projects",
        "outbox-summary",
    ]
