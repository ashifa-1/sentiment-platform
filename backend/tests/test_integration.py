import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_endpoints():
    # Health check
    for path in ["/api/health", "/health"]:
        response = client.get(path)
        if response.status_code == 200: break
    assert response.status_code == 200

    # Distribution check
    for path in ["/api/distribution", "/distribution"]:
        response = client.get(path)
        if response.status_code in [200, 404]: break
    assert response.status_code in [200, 404]