import pytest

from fastapi.testclient import TestClient

from app.api.predict import init_artifacts  # Importe la fonction d'initialisation
from app.main import app


# Charge les artefacts avant les tests
init_artifacts()


client = TestClient(app)


def test_predict_valid_client():
    payload = {"SK_ID_CURR": 100001}
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200  # noqa: PLR2004, S101
    data = response.json()
    assert "result" in data  # au lieu de "prediction"  # noqa: S101
    assert "probability_bad_customer" in data  # noqa: S101
    assert "probability_good_customer" in data  # noqa: S101
    assert data["result"].startswith((  # noqa: S101
        "✅",
        "❌",
    ))  # vérifie que le résultat commence par un emoji de validation ou d'erreur


def test_predict_invalid_client():
    payload = {"SK_ID_CURR": 999999999}  # ID qui n'existe pas
    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 404  # noqa: PLR2004, S101
    assert "Client ID" in response.json()["detail"]  # noqa: S101
