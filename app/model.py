import pickle
from pathlib import Path
import pandas as pd

MODELS_DIR = Path(__file__).parent.parent / "models"

def load_model():
    model = pickle.load(open(MODELS_DIR / "Best_LGBM_Model.pkl", "rb"))
    encoders = pickle.load(open(MODELS_DIR / "encoders.pkl", "rb"))
    features = pickle.load(open(MODELS_DIR / "model_features.pkl", "rb"))
    return model, encoders, features

def preprocess(data: dict, encoders: dict):
    # Exemple : encodage OneHot/Label selon encoders sauvegardés
    # Ici, adapter à ton vrai preprocessing
    return pd.DataFrame([data])

def predict_client(model, encoders, features, raw_data: dict):
    df = preprocess(raw_data, encoders)
    score = model.predict_proba(df[features])[:, 1][0]
    return {
        "score": float(score),
        "default_risk": score > 0.5
    }
