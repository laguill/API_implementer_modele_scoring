import pytest

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert response.json() == {"status": "ok", "message": "Credit Scoring API is running"}  # noqa: S101


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert "Credit Scoring API is running!" in response.text  # noqa: S101
    assert "<title>Credit Scoring API</title>" in response.text  # noqa: S101


def test_cors_headers():
    headers = {"Origin": "http://example.com"}  # Simule une requête cross-origin
    response = client.get("/health", headers=headers)
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert "access-control-allow-origin" in response.headers  # noqa: S101
    assert response.headers["access-control-allow-origin"] == "*"  # noqa: S101


def test_api_router_included():
    response = client.post("/api/v1/predict", json={"SK_ID_CURR": 100001})
    assert response.status_code in [200, 404]  # noqa: S101


def test_pages_router_included():
    response = client.get("/pages/")
    assert response.status_code in [200, 404]  # noqa: S101
