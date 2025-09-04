import pytest

from fastapi.testclient import TestClient

from app.main import app


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
        "⚠️",
    ))  # vérifie que le résultat commence par un emoji de validation ou d'erreur


def test_predict_invalid_client():
    payload = {"SK_ID_CURR": 999999999}  # ID qui n'existe pas
    response = client.post("/api/v1/predict", json=payload)

    assert response.status_code == 404  # noqa: PLR2004, S101
    assert "Client ID" in response.json()["detail"]  # noqa: S101


def test_check_client_exists():
    client_id = 100001
    response = client.get(f"/api/v1/check_client/{client_id}")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert response.json()["exists"] is True  # noqa: S101


def test_check_client_does_not_exist():
    client_id = 999999999  # ID inexistant
    response = client.get(f"/api/v1/check_client/{client_id}")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert response.json()["exists"] is False  # noqa: S101


def test_get_client_info_valid():
    client_id = 100001  # Remplacez par un ID client qui existe réellement
    response = client.get(f"/api/v1/client_info/{client_id}")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert isinstance(response.json(), dict)  # Vérifie que la réponse est un dictionnaire  # noqa: S101


def test_get_client_info_invalid():
    client_id = 999999999  # ID inexistant
    response = client.get(f"/api/v1/client_info/{client_id}")
    assert response.status_code == 404  # noqa: PLR2004, S101
    assert "Client not found" in response.json()["detail"]  # noqa: S101


def test_global_feature_importance():
    response = client.get("/api/v1/global_feature_importance")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert isinstance(response.json(), dict)  # Vérifie que la réponse est un dictionnaire  # noqa: S101


def test_local_feature_importance_valid_client():
    client_id = 100001  # Remplacez par un ID client qui existe réellement
    response = client.get(f"/api/v1/local_feature_importance/{client_id}")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert isinstance(response.json(), dict)  # Vérifie que la réponse est un dictionnaire  # noqa: S101


def test_local_feature_importance_invalid_client():
    client_id = 999999999  # ID inexistant
    response = client.get(f"/api/v1/local_feature_importance/{client_id}")
    assert response.status_code == 404  # noqa: PLR2004, S101
    assert "Client not found" in response.json()["detail"]  # noqa: S101


def test_shap_summary_plot_valid_client():
    client_id = 100001  # Remplacez par un ID client qui existe réellement
    response = client.get(f"/api/v1/shap_summary_plot/{client_id}")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert "shap_summary_plot" in response.json()  # noqa: S101


def test_shap_summary_plot_invalid_client():
    client_id = 999999999  # ID inexistant
    response = client.get(f"/api/v1/shap_summary_plot/{client_id}")
    assert response.status_code == 404  # noqa: PLR2004, S101
    assert "Client not found" in response.json()["detail"]  # noqa: S101


def test_add_new_client():
    new_client_data = {
        "NAME_CONTRACT_TYPE": "Cash loans",
        "CODE_GENDER": "M",
        "FLAG_OWN_CAR": "Y",
        "FLAG_OWN_REALTY": "Y",
        # Ajoutez ici d'autres champs requis pour un nouveau client
    }
    response = client.post("/api/v1/client_info", json=new_client_data)
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert "client_id" in response.json()  # noqa: S101
    assert isinstance(response.json()["client_id"], int)  # noqa: S101


def test_update_client_info_valid_client():
    client_id = 100001  # Remplacez par un ID client qui existe réellement
    update_data = {"NAME_CONTRACT_TYPE": "Revolving loans"}
    response = client.put(f"/api/v1/client_info/{client_id}", json=update_data)
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert f"Informations du client {client_id} mises à jour" in response.json()["message"]  # noqa: S101


def test_update_client_info_invalid_client():
    client_id = 999999999  # ID inexistant
    update_data = {"NAME_CONTRACT_TYPE": "Revolving loans"}
    response = client.put(f"/api/v1/client_info/{client_id}", json=update_data)
    assert response.status_code == 404  # noqa: PLR2004, S101
    assert "Client not found" in response.json()["detail"]  # noqa: S101
