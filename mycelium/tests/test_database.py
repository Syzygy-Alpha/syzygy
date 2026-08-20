from syzygy_mycelium.database import Database


def test_database_initializes_peer_registry_schema() -> None:
    database = Database("sqlite:///:memory:")

    database.initialize()

    assert database.schema_version() == 1
