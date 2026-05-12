import os
import pytest
from fastapi.testclient import TestClient

os.environ["DEMO_CONFIG_PATH"] = r"C:\JUNHA\11.code\project\demoday\config\demo_data.yaml"

from app.main import app  # noqa: E402


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
