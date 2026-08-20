from syzygy_nerv.module import nerv_descriptor


def test_nerv_descriptor() -> None:
    descriptor = nerv_descriptor("0.1.0")

    assert descriptor.name == "nerv"
    assert descriptor.version == "0.1.0"
    assert descriptor.status == "online"
    assert descriptor.health.status == "ok"
    assert "dashboard" in descriptor.capabilities
    assert "forge_project_workbench" in descriptor.capabilities
    assert "module_launcher" in descriptor.capabilities
