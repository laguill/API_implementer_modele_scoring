import marimo

__generated_with = "0.15.0"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import pandas as pd
    from pathlib import Path
    import requests
    import logging
    return Path, logging, mo, pd, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Bienvenue dans le dashboard !""")
    return


@app.cell
def _(Path, logging, pd):
    # Logging config
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)

    MODELS_DIR = Path("models")

    CUSTOMERS_PATH = MODELS_DIR / "customers_data.csv"

    customers_df = pd.read_csv(
        CUSTOMERS_PATH,
    )
    customers_df.set_index("SK_ID_CURR", inplace=True)

    print("Model, encoders and customer data loaded successfully")
    print(customers_df.index[:10])
    return


@app.cell
def _(mo):
    BASE_URL = "http://localhost:7860/api/v1/predict"

    client_dropdown = mo.ui.dropdown(
        options=[100002, 100003, 100004, 100005],
        label="Sélectionner un client",
    )
    run = mo.ui.run_button(label="Faire une prédiction")

    # Afficher les contrôles
    mo.vstack([client_dropdown, run])
    return BASE_URL, client_dropdown, run


@app.cell
def _(BASE_URL, client_dropdown, mo, requests, run):
    # Logique déclenchée par le bouton
    if run.value:
        payload = {"SK_ID_CURR": client_dropdown.value}
        try:
            resp = requests.post(BASE_URL, json=payload, timeout=15)
            if resp.status_code == 200:
                mo.ui.text_area(str(resp.json()), label="Résultat", full_width=True, rows=8)
            else:
                mo.ui.text_area(f"Erreur {resp.status_code}: {resp.text}", label="Erreur", full_width=True, rows=8)
        except Exception as e:
            mo.ui.text_area(f"Erreur de connexion: {e}", label="Erreur", full_width=True, rows=8)
    else:
        mo.md("Cliquez sur le bouton pour lancer la prédiction.")
    return


if __name__ == "__main__":
    app.run()
