from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def api() -> Generator[TestClient, None, None]:
    with TestClient(app) as client:
        yield client
