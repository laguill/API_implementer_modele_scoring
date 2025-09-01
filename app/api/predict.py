import logging
import pickle

from pathlib import Path

import pandas as pd

from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel


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
model = None
encoders = None
model_features = None
customers_df = None

# --- Paths ---
MODELS_DIR = Path(__file__).parent.parent.parent / "models"
MODEL_PATH = MODELS_DIR / "Best_LGBM_Model.pkl"
ENCODERS_PATH = MODELS_DIR / "encoders.pkl"
FEATURES_PATH = MODELS_DIR / "model_features.pkl"
CUSTOMERS_PATH = MODELS_DIR / "customers_data.csv"


def init_artifacts():
    """Load all ML artifacts from disk."""
    global model, encoders, model_features, customers_df  # noqa: PLW0603

    with Path.open(MODEL_PATH, "rb") as f:
        model = pickle.load(f)  # noqa: S301
    with Path.open(ENCODERS_PATH, "rb") as f:
        encoders = pickle.load(f)  # noqa: S301
    with Path.open(FEATURES_PATH, "rb") as f:
        model_features = pickle.load(f)  # noqa: S301
    customers_df = pd.read_csv(CUSTOMERS_PATH, index_col="SK_ID_CURR")

    logger.info("✅ Model, encoders and customer data loaded successfully")


# Helper function to preprocess a client
def preprocess_client(client_id: int):
    if customers_df is None:
        msg = "Artifacts not loaded. Did you forget to call init_artifacts()?"
        raise RuntimeError(msg)

    if client_id not in customers_df.index:
        msg = f"Client ID {client_id} not found"
        raise ValueError(msg)

    client_data = customers_df.loc[[client_id]].copy()

    # Appliquer les encoders
    for col, enc in encoders.items():  # pyright: ignore[reportOptionalMemberAccess]
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
    missing_cols = [c for c in model_features if c not in client_data.columns]  # pyright: ignore[reportOptionalIterable]
    for c in missing_cols:
        client_data[c] = 0

    client_data = client_data[model_features]
    return client_data


# Prediction endpoint
@router.post("/predict", summary="Predict credit default risk for a client")
async def predict(client: ClientInput):
    try:
        if customers_df is None or model is None:
            raise HTTPException(status_code=500, detail="🚨 Model artifacts are not loaded")  # noqa: TRY301

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
            "✅ Good customer, offer him his credit !" if result == 0 else "⚠️ Bad customer, offer him a coffee !"
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
