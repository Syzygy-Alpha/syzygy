from datetime import UTC, datetime

from syzygy_observatory.database import Database
from syzygy_observatory.health_observations import (
    HealthObservationRequest,
    HealthObservationStore,
)


def build_store() -> HealthObservationStore:
    database = Database("sqlite:///:memory:")
    database.initialize()
    return HealthObservationStore(database)


def test_health_observation_store_records_observation() -> None:
    store = build_store()

    record = store.record(
        HealthObservationRequest(
            name="forge",
            status="ok",
            source="manual",
            details={"url": "http://127.0.0.1:8010/health"},
            observed_at=datetime(2026, 8, 11, 12, 0, tzinfo=UTC),
        )
    )

    assert record.id == 1
    assert record.name == "forge"
    assert record.status == "ok"
    assert record.details["url"] == "http://127.0.0.1:8010/health"


def test_health_observation_store_lists_with_filters() -> None:
    store = build_store()
    store.record(HealthObservationRequest(name="forge", status="ok"))
    store.record(HealthObservationRequest(name="foundation", status="degraded"))

    ok_records = store.list_observations(status="ok")
    foundation_records = store.list_observations(name="foundation")

    assert [record.name for record in ok_records] == ["forge"]
    assert [record.status for record in foundation_records] == ["degraded"]


def test_health_observation_store_summarizes_latest_by_name() -> None:
    store = build_store()
    store.record(HealthObservationRequest(name="forge", status="ok"))
    store.record(HealthObservationRequest(name="foundation", status="ok"))
    store.record(HealthObservationRequest(name="forge", status="degraded"))

    summary = store.summary()

    assert summary.total == 3
    assert summary.by_status == {"degraded": 1, "ok": 2}
    assert [(record.name, record.status) for record in summary.latest_by_name] == [
        ("forge", "degraded"),
        ("foundation", "ok"),
    ]
