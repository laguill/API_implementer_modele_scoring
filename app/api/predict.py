from fastapi import APIRouter, HTTPException
from pathlib import Path
from pydantic import BaseModel
from pathlib import Path
import pickle
import pandas as pd
import logging

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


# --- Load model artifacts once ---
MODELS_DIR = Path(__file__).parent.parent.parent / "models"

MODEL_PATH = MODELS_DIR / "Best_LGBM_Model.pkl"
ENCODERS_PATH = MODELS_DIR / "encoders.pkl"
FEATURES_PATH = MODELS_DIR / "model_features.pkl"
CUSTOMERS_PATH = MODELS_DIR / "customers_data.csv"

with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

with open(ENCODERS_PATH, "rb") as f:
    encoders = pickle.load(f)

with open(FEATURES_PATH, "rb") as f:
    model_features = pickle.load(f)

customers_df = pd.read_csv(CUSTOMERS_PATH, index_col="SK_ID_CURR")

logger.info("Model, encoders and customer data loaded successfully")


# Helper function to preprocess a client
def preprocess_client(client_id: int):
    if client_id not in customers_df.index:
        raise ValueError(f"Client ID {SK_ID_CURR} not found")

    client_data = customers_df.loc[[client_id]].copy()  # dataframe d’une seule ligne

    # Appliquer les encoders
    for col, enc in encoders.items():
        if col in client_data.columns:
            if hasattr(enc, "transform"):  # LabelEncoder ou OneHotEncoder
                try:
                    transformed = enc.transform(client_data[[col]])
                    if transformed.ndim == 1:  # LabelEncoder
                        client_data[col] = transformed
                    else:  # OneHotEncoder
                        # créer colonnes OHE
                        ohe_df = pd.DataFrame(
                            transformed,
                            columns=[f"{col}_{c}" for c in enc.categories_[0]],
                            index=client_data.index,
                        )
                        client_data.drop(columns=[col], inplace=True)
                        client_data = pd.concat([client_data, ohe_df], axis=1)
                except Exception as e:
                    logger.error(f"Encoding failed for column {col}: {e}")
                    raise

    # Garder uniquement les colonnes attendues par le modèle
    missing_cols = [c for c in model_features if c not in client_data.columns]
    for c in missing_cols:
        client_data[c] = 0  # remplir les colonnes manquantes si nécessaire

    client_data = client_data[model_features]  # réordonner les colonnes

    return client_data

# Prediction endpoint
@router.post("/predict", summary="Predict credit default risk for a client")
async def predict(client: ClientInput):
    try:
        # Vérifie si l'ID existe dans la base
        if client.SK_ID_CURR not in customers_df.index:
            raise HTTPException(
                status_code=404,
                detail=f"❌ Client ID {client.SK_ID_CURR} not found in database. "
                       f"Please provide a valid SK_ID_CURR."
            )

        # Prétraitement
        X = preprocess_client(client.SK_ID_CURR)

        # Prédiction
        results = model.predict_proba(X)
        result = model.predict(X)

        good_customer_proba = float(results[0][0])
        bad_customer_proba = float(results[0][1])

        translated_result = (
            "✅ Good customer, offer him his credit !"
            if result == 0
            else "⚠️ Bad customer, offer him a coffee !"
        )

        return {
            "client_id": client.SK_ID_CURR,
            "probability_good_customer": good_customer_proba,
            "probability_bad_customer": bad_customer_proba,
            "result": translated_result,
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"🚨 Prediction failed for client {client.SK_ID_CURR}: {str(e)}"
        )
