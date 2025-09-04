import atexit
import os
import shutil
import tempfile

from pathlib import Path

from app.api import predict


# --- Crée un CSV temporaire pour toute la session ---
temp_dir = Path(tempfile.mkdtemp())
temp_file = temp_dir / "customers_data.csv"
shutil.copy(Path("models/customers_data.csv"), temp_file)

# --- Surcharge la variable globale et la variable d'environnement ---
os.environ["CUSTOMERS_PATH"] = str(temp_file)  # chaîne pour os.getenv
predict.CUSTOMERS_PATH = temp_file  # Path pour predict.py

# --- Initialise les artefacts une seule fois pour tous les tests ---
predict.init_artifacts()


# --- Nettoyage du dossier temporaire à la fin de la session ---
def cleanup_temp_dir():
    shutil.rmtree(temp_dir)


atexit.register(cleanup_temp_dir)
