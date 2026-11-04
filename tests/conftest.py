import atexit
import os
import shutil
import tempfile

# Settings are read once, when the app is first imported, so the test database
# and secret key must be in the environment before any app module is imported.
# TEST_DATABASE_URL runs the tests on another database, such as PostgreSQL in CI.
_db_dir = tempfile.mkdtemp(prefix="cognicortex-tests-")
atexit.register(shutil.rmtree, _db_dir, ignore_errors=True)
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL", f"sqlite:///{os.path.join(_db_dir, 'test.db')}"
)
os.environ["SECRET_KEY"] = "test-secret-key-at-least-32-bytes-long"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db.base import Base  # noqa: E402
from app.db.session import engine  # noqa: E402
from app.main import app  # noqa: E402
from app.workers.celery_app import celery_app  # noqa: E402

# Run Celery tasks immediately in this process instead of sending them to Redis.
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)


@pytest.fixture(autouse=True)
def fresh_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def register_and_login(client):
    def _register_and_login(email="owner@example.com", password="correct-horse"):
        client.post(
            "/api/v1/users",
            json={
                "email": email,
                "username": email.split("@")[0],
                "name": "Test User",
                "password": password,
            },
        )
        response = client.post(
            "/api/v1/auth/login", data={"username": email, "password": password}
        )
        return {"Authorization": f"Bearer {response.json()['access_token']}"}

    return _register_and_login


@pytest.fixture
def auth_headers(register_and_login):
    return register_and_login()
