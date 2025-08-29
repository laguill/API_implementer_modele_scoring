from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.predict import router as api_router
from app.api.pages import router as pages_router, pages

from pathlib import Path
import marimo
import logging
import os
from dotenv import load_dotenv

# Logging
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",)
logger = logging.getLogger(__name__)

# Variables d'environnement
load_dotenv()
PORT = int(os.environ.get("PORT", 7860))

# Application FastAPI
app = FastAPI(
    title="Credit Scoring API",
    description="API to predict credit default risk and serve interactive dashboards",
    version="1.0.0"
)

# Ajout du middleware pour gérer CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Autorise toutes les origines
    allow_credentials=True,
    allow_methods=["*"],  # Autorise toutes les méthodes HTTP
    allow_headers=["*"],  # Autorise tous les headers
)

# Charger les routes API principales
app.include_router(api_router) # API endpoints (predictions, etc)

# Marimo dashboards
app.include_router(pages_router)

# Health check endpoint (API-friendly)
@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "ok", "message": "Credit Scoring API is running"}

# Configurer Marimo
PAGES_DIR = Path(__file__).parent.parent / "pages"
server = marimo.create_asgi_app(include_code=True)

if PAGES_DIR.exists():
    for file in PAGES_DIR.glob("*.py"):
        page_name = file.stem
        server = server.with_app(path=f"/{page_name}", root=str(file))
        pages.append(page_name)

    logger.info(f"Mounting dashboards: {pages}")
    # Montage de l'app ASGI Marimo
    app.mount("/pages", server.build())
else:
    logger.warning("No pages directory found, skipping dashboard mounting")

# Homepage (human-friendly)
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Credit Scoring API</title>
    </head>
    <body>
        <h1>✅ Credit Scoring API is running!</h1>
        <p>Welcome to the API for credit scoring and interactive dashboards built with Marimo.</p>
        <h2>Useful Links</h2>
        <ul>
            <li><a href="/docs">Swagger UI</a> (interactive API docs)</li>
            <li><a href="/redoc">ReDoc</a> (alternative API docs)</li>
            <li><a href="/pages/index">Dashboards</a> (Marimo apps)</li>
            <li><a href="/health">Health check</a> (API status)</li>
        </ul>
    </body>
    </html>
    """

# Point d'entrée local
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=PORT, reload=True)
