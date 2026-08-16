from syzygy_observatory.module import observatory_descriptor


def test_observatory_descriptor() -> None:
    descriptor = observatory_descriptor("0.1.0")

    assert descriptor.name == "observatory"
    assert descriptor.version == "0.1.0"
    assert descriptor.status == "online"
    assert descriptor.health.status == "ok"
    assert descriptor.dependencies == ["foundation"]
    assert "foundation_module_ingestion" in descriptor.capabilities
    assert "foundation_module_polling" in descriptor.capabilities
    assert "health_observation_storage" in descriptor.capabilities
    assert "health_summary" in descriptor.capabilities
    assert "health_trends" in descriptor.capabilities
