import marimo


__generated_with = "0.15.1"
app = marimo.App()


@app.cell
def _():
    import logging

    from pathlib import Path

    import marimo as mo
    import pandas as pd
    import requests

    from requests.exceptions import RequestException

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
    logging.getLogger(__name__)

    MODELS_DIR = Path("models")

    CUSTOMERS_PATH = MODELS_DIR / "customers_data.csv"

    customers_df = pd.read_csv(CUSTOMERS_PATH, index_col="SK_ID_CURR")

    print("Model, encoders and customer data loaded successfully")
    print(customers_df.index[:10])
    return (customers_df,)


@app.cell
def _(customers_df, mo):
    BASE_URL = "http://localhost:7860/api/v1/predict"

    client_dropdown = mo.ui.dropdown(
        options=customers_df.index[:10],
        label="Sélectionner un client",
    )
    run = mo.ui.run_button(label="Faire une prédiction", full_width=True)

    mo.vstack([client_dropdown, run])
    return BASE_URL, client_dropdown, run


@app.cell
def _(BASE_URL, client_dropdown, mo, requests, run):
    # logique déclenchée par le bouton
    panel = mo.output
    panel  # affiche le conteneur  # pyright: ignore[reportUnusedExpression]

    if run.value:
        payload = {"SK_ID_CURR": client_dropdown.value}
        try:
            resp = requests.post(BASE_URL, json=payload, timeout=15)
            if resp.status_code == 200:  # noqa: PLR2004
                panel.replace(
                    mo.ui.text_area(
                        str(resp.json()),
                        label="Résultat",
                        full_width=True,
                        rows=8,
                    )
                )
            else:
                panel.replace(
                    mo.ui.text_area(
                        f"Erreur {resp.status_code}: {resp.text}",
                        label="Erreur",
                        full_width=True,
                        rows=8,
                    )
                )
        except RequestException as e:
            panel.replace(
                mo.ui.text_area(
                    f"Erreur de connexion: {e}",
                    label="Erreur",
                    full_width=True,
                    rows=8,
                )
            )
    else:
        panel.replace(mo.md("Cliquez sur le bouton pour lancer la prédiction."))
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
