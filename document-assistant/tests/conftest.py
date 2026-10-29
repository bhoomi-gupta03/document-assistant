import pytest
from fastapi.testclient import TestClient

from app.database import connect, get_db, init_db
from app.main import app


@pytest.fixture
def db_path(tmp_path):
    """A fresh, empty SQLite file for every test (never your real database)."""
    path = str(tmp_path / "test.db")
    init_db(path)
    return path


@pytest.fixture
def conn(db_path):
    connection = connect(db_path)
    yield connection
    connection.close()


@pytest.fixture
def client(db_path):
    def override_get_db():
        connection = connect(db_path)
        try:
            yield connection
        finally:
            connection.close()

    app.dependency_overrides[get_db] = override_get_db
    # No "with" block on purpose: the startup hook is skipped, so the app
    # never creates documents.db during tests.
    yield TestClient(app)
    app.dependency_overrides.clear()
