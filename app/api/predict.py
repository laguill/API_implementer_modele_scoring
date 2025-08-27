from fastapi import APIRouter, HTTPException
from pathlib import Path
from pydantic import BaseModel
import pickle
import logging

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Prediction"])

# Schéma d'entrée pour la prédiction
class PredictionInput(BaseModel):
    feature1: float
    feature2: float
    # ajoute tes autres features ici

# Charger le modèle 1 seule fois (pas à chaque requête)
MODEL_PATH = Path(__file__).parent.parent.parent / "models" / "Best_LGBM_Model.pkl"
with open(MODEL_PATH, "rb") as f:
    model = pickle.load(f)

logger.info("Model loaded successfully from %s", MODEL_PATH)

@router.post("/predict", summary="Make a prediction")
async def predict(input: PredictionInput):
    try:
        prediction = model.predict([[input.feature1, input.feature2]])
        return {"prediction": int(prediction[0])}
    except Exception as e:
        logger.error("Prediction failed: %s", e)
        raise HTTPException(status_code=500, detail="Prediction failed")
