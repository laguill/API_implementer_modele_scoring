import marimo


__generated_with = "0.15.2"
app = marimo.App()


@app.cell
def _():
    import logging

    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd
    import requests
    import seaborn as sns

    from requests.exceptions import RequestException

    return Path, RequestException, mo, pd, plt, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Prêt à dépenser -- Accord de prêt""")
    return


@app.cell
def _(mo):
    mo.image("logo.png")
    return


@app.cell
def _(Path, pd):
    # charge les données du fichier csv
    MODELS_DIR = Path("models")

    CUSTOMERS_PATH = MODELS_DIR / "customers_data.csv"

    customers_df = pd.read_csv(CUSTOMERS_PATH, index_col="SK_ID_CURR")

    print("Model, encoders and customer data loaded successfully")
    return (customers_df,)


@app.cell
def _(customers_df, mo):
    # BASE_URL = "http://localhost:7860/api/v1/predict"  # noqa: ERA001
    BASE_URL = "https://laguill-implementer-model-scoring.hf.space/api/v1/predict"

    client_dropdown = mo.ui.dropdown(
        options=customers_df.index[:10],
        label="Sélectionner un client",
    )
    run = mo.ui.run_button(label="Faire une prédiction", full_width=True)

    mo.vstack([client_dropdown, run])
    return BASE_URL, client_dropdown, run


@app.cell
def _(BASE_URL, RequestException, client_dropdown, mo, requests, run):
    # logique déclenchée par le bouton
    panel = mo.output
    panel  # affiche le conteneur  # pyright: ignore[reportUnusedExpression]

    with mo.status.spinner(subtitle="Loading data ...") as _spinner:
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
    return (resp,)  # pyright: ignore[reportPossiblyUnboundVariable]


@app.cell
def _(mo, plt, resp):
    prediction_data = resp.json()

    # Accès aux éléments du JSON
    client_id = prediction_data["client_id"]
    prob_good = prediction_data["probability_good_customer"]
    prob_bad = prediction_data["probability_bad_customer"]
    result = prediction_data["result"]

    # Affichage des informations dans le dashboard
    mo.md(f"""
    ### Résultats de la prédiction pour le client {client_id}

    - Probabilité de bon client: {prob_good:.2%}
    - Probabilité de mauvais client: {prob_bad:.2%}
    - Résultat: {result}
    """)

    # Création d'un graphique pour visualiser les probabilités
    plt.figure(figsize=(6, 4))
    plt.bar(["Bon client", "Mauvais client"], [prob_good, prob_bad], color=["green", "red"])
    plt.title(f"Probabilités pour le client {client_id}")
    plt.ylabel("Probabilité")
    plt.ylim(0, 1)
    plt.gca()  # Retourne les axes pour l'affichage
    return


if __name__ == "__main__":
    app.run()
