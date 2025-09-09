import base64
import logging
import os
import pickle

from io import BytesIO
from pathlib import Path
from typing import Annotated, Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

from fastapi import APIRouter, Body, FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.pipeline import Pipeline


# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Prediction"])


# Input model
class ClientInput(BaseModel):
    SK_ID_CURR: int


# --- Global variables for artifacts ---
model: Pipeline
encoders: dict[str, Any] = {}
model_features: list[str] = []
customers_df: pd.DataFrame = pd.DataFrame()
explainer: shap.Explainer
global_shap_importance: pd.DataFrame = pd.DataFrame()

# --- Paths ---
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_PATH = MODELS_DIR / "Best_LGBM_Model.pkl"
ENCODERS_PATH = MODELS_DIR / "encoders.pkl"
FEATURES_PATH = MODELS_DIR / "model_features.pkl"

# Permet de surcharger le chemin dans les tests avec une variable d'environnement
CUSTOMERS_PATH = Path(os.getenv("CUSTOMERS_PATH", MODELS_DIR / "customers_data.csv"))


def init_artifacts():
    """Load all ML artifacts from disk."""
    global model, encoders, model_features, customers_df, explainer, global_shap_importance  # noqa: PLW0603

    with Path.open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)  # noqa: S301
    with Path.open(ENCODERS_PATH, "rb") as f:
        encoders = pickle.load(f)  # noqa: S301
    with Path.open(FEATURES_PATH, "rb") as f:
        model_features = pickle.load(f)  # noqa: S301
    customers_df = pd.read_csv(CUSTOMERS_PATH, index_col="SK_ID_CURR")

    # --- Prétraitement global (tous les clients encodés)
    processed_clients = []
    for client_id in customers_df.index[:1000]:  # limite si dataset trop gros
        try:
            X = preprocess_client(client_id)
            processed_clients.append(X)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Skipping client {client_id}: {e}")  # noqa: G004

    if not processed_clients:
        msg = "⚠️ Impossible de construire SHAP : aucun client valide après prétraitement"
        raise RuntimeError(msg)

    full_X = pd.concat(processed_clients)

    # Extract the final model (LightGBM) from the pipeline
    lgbm_model = model.named_steps["model"]

    # Créer explainer avec les données prétraitées
    explainer = shap.Explainer(lgbm_model)
    shap_values_train = explainer(full_X)

    global_values = np.abs(shap_values_train.values).mean(axis=0)
    global_shap_importance = pd.DataFrame(
        list(zip(model_features, global_values, strict=False)),
        columns=["feature", "importance"],  # pyright: ignore[reportArgumentType]
    ).sort_values(by="importance", ascending=False)

    logger.info("✅ Model, encoders, SHAP and customer data loaded successfully")


# Helper function to preprocess a client
def preprocess_client(client_id: int):
    if client_id not in customers_df.index:
        msg = f"Client ID {client_id} not found"
        raise ValueError(msg)

    client_data = customers_df.loc[[client_id]].copy()

    # Appliquer les encoders
    for col, enc in encoders.items():
        if col in client_data.columns and hasattr(enc, "transform"):
            try:
                if enc.__class__.__name__ == "LabelEncoder":
                    transformed = enc.transform(client_data[col])
                    client_data[col] = transformed
                else:
                    transformed = enc.transform(client_data[[col]])
                    ohe_df = pd.DataFrame(
                        transformed,
                        columns=[f"{col}_{c}" for c in enc.categories_[0]],  # pyright: ignore[reportArgumentType]
                        index=client_data.index,
                    )
                    client_data = client_data.drop(columns=[col])
                    client_data = pd.concat([client_data, ohe_df], axis=1)
            except Exception:
                logger.exception(f"Encoding failed for column {col}")  # noqa: G004
                raise

    # Garder uniquement les colonnes attendues par le modèle
    missing_cols = [c for c in model_features if c not in client_data.columns]
    for c in missing_cols:
        client_data[c] = 0

    client_data = client_data[model_features]
    return client_data[model_features]


# Prediction endpoint
@router.post("/predict", summary="Predict credit default risk for a client")
async def predict(client: ClientInput):
    try:
        if client.SK_ID_CURR not in customers_df.index:
            raise HTTPException(  # noqa: TRY301
                status_code=404,
                detail=f"❌ Client ID {client.SK_ID_CURR} not found in database. Please provide a valid SK_ID_CURR.",
            )

        X = preprocess_client(client.SK_ID_CURR)

        results = model.predict_proba(X)
        result = model.predict(X)

        good_customer_proba = float(results[0][0])
        bad_customer_proba = float(results[0][1])

        translated_result = (
            "✅ Bon client, proposez lui un credit !" if result == 0 else "⚠️ Mauvais client, offrez lui un café !"
        )

        return {  # noqa: TRY300
            "client_id": client.SK_ID_CURR,
            "probability_good_customer": good_customer_proba,
            "probability_bad_customer": bad_customer_proba,
            "result": translated_result,
        }
    except HTTPException:
        raise
    except Exception as e:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=f"🚨 Prediction failed for client {client.SK_ID_CURR}: {e!s}")  # noqa: B904


@router.get("/check_client/{client_id}")
async def check_client(client_id: int):
    return {"exists": bool(client_id in customers_df.index)}


@router.get("/client_info/{client_id}")
async def get_client_info(client_id: int):
    if client_id not in customers_df.index:
        raise HTTPException(status_code=404, detail="Client not found")

    return customers_df.loc[client_id].replace({np.nan: None}).to_dict()


@router.get("/global_feature_importance")
async def global_feature_importance():
    return global_shap_importance.head(10).set_index("feature")["importance"].to_dict()


@router.get("/local_feature_importance/{client_id}")
async def local_feature_importance(client_id: int):
    if client_id not in customers_df.index:
        raise HTTPException(status_code=404, detail="Client not found")

    X = preprocess_client(client_id)
    shap_values = explainer(X, check_additivity=False)
    local_values = np.abs(shap_values.values[0])  # noqa: PD011

    local_importance = pd.DataFrame(
        list(zip(model_features, local_values, strict=False)),
        columns=["feature", "importance"],  # pyright: ignore[reportArgumentType]
    ).sort_values(by="importance", ascending=False)

    return local_importance.set_index("feature")["importance"].to_dict()


@router.get("/shap_summary_plot/{client_id}")
async def shap_summary_plot(client_id: int):
    if client_id not in customers_df.index:
        raise HTTPException(status_code=404, detail="Client not found")

    X = preprocess_client(client_id)
    shap_values = explainer(X)

    shap.plots.waterfall(shap_values[0], max_display=10, show=False)
    plt.tight_layout()

    buf = BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

    return {"shap_summary_plot": image_base64}


@router.post("/client_info", summary="Ajouter un nouveau client")
async def submit_new_client(data: Annotated[dict, Body()] = ...):  # pyright: ignore[reportMissingTypeArgument, reportArgumentType]
    global customers_df  # noqa: PLW0603

    # Générer un nouvel ID unique
    new_client_id = int(customers_df.index.max()) + 1 if not customers_df.empty else 1  # pyright: ignore[reportArgumentType]
    data["SK_ID_CURR"] = new_client_id

    # Ajouter le client dans le DataFrame
    new_row = pd.DataFrame([data]).set_index("SK_ID_CURR")
    customers_df = pd.concat([customers_df, new_row], axis=0)

    # Sauvegarder si tu veux persister
    customers_df.to_csv(CUSTOMERS_PATH)

    return {"message": "✅ Nouveau client ajouté avec succès", "client_id": new_client_id}


@router.put("/client_info/{client_id}", summary="Mettre à jour les informations d'un client")
async def update_client_info(client_id: int, data: Annotated[dict[str, Any], Body(...)]):
    global customers_df  # noqa: PLW0602

    if client_id not in customers_df.index:
        raise HTTPException(status_code=404, detail="❌ Client not found")

    # Mise à jour des colonnes
    for key, value in data.items():
        if key in customers_df.columns:
            customers_df.loc[client_id, key] = value
        else:
            # Ajouter la colonne si elle n'existait pas
            customers_df[key] = None
            customers_df.loc[client_id, key] = value

    # Sauvegarde
    customers_df.to_csv(CUSTOMERS_PATH)

    return {"message": f"✅ Informations du client {client_id} mises à jour avec succès"}
