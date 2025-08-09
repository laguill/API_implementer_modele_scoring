from fastapi import FastAPI
import marimo
from app.api import register_routes
import logging
from pathlib import Path

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Répertoire contenant les notebooks Marimo
PAGES_DIR = Path(__file__).parent / "pages"

# Création de l'app Marimo
server = marimo.create_asgi_app(include_code=True)
app_names: list[str] = []

if PAGES_DIR.exists():
    for filename in PAGES_DIR.iterdir():
        if filename.is_file() and filename.suffix == ".py":
            app_path = f"{PAGES_DIR.stem}/{filename.stem}"
            server = server.with_app(path=f"/{app_path}", root=str(filename))
            app_names.append(app_path)

# Création de l'app FastAPI
app = FastAPI(title="Credit Scoring API", version="1.0")

# Enregistrement des routes FastAPI classiques
register_routes(app)

logger.info(f"Mounting {len(app_names)} Marimo apps")
for name in app_names:
    logger.info(f"  /{name}")

# Montage des apps Marimo sous /dashboard
app.mount("/pages", server.build())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860, log_level="info")
