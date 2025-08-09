from fastapi import FastAPI
from app.api import register_routes
import marimo
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Credit Scoring API",
    description="API to predict credit default risk and serving dashboards",
    version="1.0.0"
)

# Load APi endpoints
register_routes(app)

# Confifigure Marimo to server dashboards
PAGES_DIR = Path(__file__).parent / "pages"
server = marimo.create_asgi_app(include_code=True)
pages = []

for file in PAGES_DIR.glob("*.py"):
    page_name = file.stem
    server = server.with_app(path=f"/{page_name}", root=str(file))
    pages.append(page_name)

logger.info(f"Mounting pages: {pages}")
app.mount("/pages", server.build())

# Endpoints to list dashboards
@app.get("/pages", tags=["PAGES"])
def list_dashboards():
    return {"available_pages": [f"/page/{name}" for name in pages]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=7860, log_level="info")
