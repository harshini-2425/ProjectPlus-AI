import os

os.environ.setdefault("USE_SQLITE_FOR_TESTS", "true")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    from backend.app.db.database import Base, engine

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
