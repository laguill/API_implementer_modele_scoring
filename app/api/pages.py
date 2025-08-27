from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s - %(message)s")
logger = logging.getLogger(__name__)

logger.info("Mounting pages")

# Router uniquement pour exposer la liste des dashboards en JSON
router = APIRouter(tags=["Pages"])

# Variable partagée (remplie dans main.py)
pages: list[str] = []

@router.get("/pages")
def list_dashboards():
    """Retourne la liste des dashboards disponibles"""
    return {"available_pages": [f"/pages/{name}" for name in pages]}

# --- HTML endpoint (utile pour visiteurs humains) ---
@router.get("/index", response_class=HTMLResponse, include_in_schema=False)
async def list_dashboards_html():
    links = "".join([f'<li><a href="/pages/{name}">{name}</a></li>' for name in pages])
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Available Dashboards</title>
    </head>
    <body>
        <h1>📊 Available Dashboards</h1>
        <ul>
            {links}
        </ul>
    </body>
    </html>
    """
    return html_content
