from fastapi import FastAPI
from marimo import create_asgi_app
from app.api import register_routes

# Crée l'app FastAPI principale
app = FastAPI()

# Enregistre tes propres routes FastAPI
register_routes(app)

# Serve the marimo notebook at /dashboard
server = create_asgi_app().with_app(path="", root="pages/dashboard.py")
app.mount("/dashboard", server.build())

# Point d’entrée (optionnel si tu lances via uvicorn)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=7860)


# Run with: uvicorn api:app --host 0.0.0.0 --port 7860
