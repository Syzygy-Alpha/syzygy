from syzygy_observatory.database import Database


def test_database_initializes_schema() -> None:
    database = Database("sqlite:///:memory:")

    database.initialize()

    assert database.schema_version() == 1
