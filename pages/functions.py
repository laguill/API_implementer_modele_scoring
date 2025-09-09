import base64

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests

from requests.exceptions import RequestException


# charge les données du fichier csv
MODELS_DIR = Path("models")

CUSTOMERS_PATH = MODELS_DIR / "customers_data.csv"

customers_df = pd.read_csv(CUSTOMERS_PATH, index_col="SK_ID_CURR")

BASE_URL = "http://localhost:7860/api/v1"
# BASE_URL = "https://laguill-implementer-model-scoring.hf.space/api/v1" # noqa: ERA001


def run_prediction(client_id):
    data = {"SK_ID_CURR": client_id}
    try:
        resp = requests.post(
            f"{BASE_URL}/predict",
            json=data,
            timeout=15,
        )
        resp.raise_for_status()
    except RequestException as e:
        return f"Erreur de connexion: {e}"
    else:
        return resp


def get_client_info(client_id):
    url = f"{BASE_URL}/client_info/{client_id}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return f"Erreur lors de l'obtention des informations du client: {e}"


def update_client_info(client_id, data):
    response = requests.put(f"{BASE_URL}/client_info/{client_id}", json=data, timeout=15)
    if response.status_code == 200:  # noqa: PLR2004
        print("Informations du client mises à jour")
        return True
    print(f"Erreur lors de la mise à jour des informations du client: {response.text}")
    return False


def get_shap_summary_plot(client_id):
    try:
        response = requests.get(f"{BASE_URL}/shap_summary_plot/{client_id}", timeout=15)
        response.raise_for_status()
        shap_plot_data = response.json().get("shap_summary_plot")
        if shap_plot_data:
            return base64.b64decode(shap_plot_data)

    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'obtention du SHAP summary plot: {e}")
        return None


def get_global_feature_importance():
    try:
        response = requests.get(f"{BASE_URL}/global_feature_importance", timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'obtention de la feature importance globale: {e}")
        return None


def get_local_feature_importance(client_id):
    try:
        response = requests.get(f"{BASE_URL}/local_feature_importance/{client_id}", timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de l'obtention de la feature importance locale: {e}")
        return None
