from fastapi import FastAPI
from pydantic import BaseModel

def register_routes(app: FastAPI):

    @app.get("/", tags=["General"])
    def home():
        return {"message": "Bienvenue sur mon API FastAPI"}

    @app.get("/status", tags=["General"])
    def status():
        return {"status": "OK"}

    class Features(BaseModel):
        # Remplace par tes vraies features
        feature1: float
        feature2: int

    @app.post("/predict", tags=["Prediction"])
    def predict(features: Features):
        # Ici tu appelles ta fonction score, modèle etc.
        result = {"risk_score": 0.75, "default": False}
        return result
