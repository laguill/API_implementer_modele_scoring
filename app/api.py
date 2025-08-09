from fastapi import FastAPI
from pydantic import BaseModel
from app.model import load_model, predict_client

model, encoders, features = load_model()

def register_routes(app: FastAPI):
    @app.get("/", tags=["General"])
    def home():
        return {"message": "Welcome to the Credit Scoring API"}

    @app.get("/status", tags=["General"])
    def status():
        return {"status": "OK"}

    class Features(BaseModel):
        # Adapte à tes features réelles
        feature1: float
        feature2: int

    @app.post("/predict", tags=["Prediction"])
    def predict(data: Features):
        prediction = predict_client(model, encoders, features, data.dict())
        return prediction
