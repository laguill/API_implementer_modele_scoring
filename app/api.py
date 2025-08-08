from fastapi import FastAPI

def register_routes(app: FastAPI):
    @app.get("/")
    def home():
        return {"message": "Bienvenue sur mon API FastAPI"}

    @app.get("/status")
    def status():
        return {"status": "OK"}
