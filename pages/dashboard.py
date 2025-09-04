import marimo


__generated_with = "0.15.2"
app = marimo.App()


@app.cell
def _():
    import logging

    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import requests
    import seaborn as sns

    from requests.exceptions import RequestException

    return Path, RequestException, go, mo, np, pd, plt, px, requests


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Prêt à dépenser -- Accord de prêt""")
    return


@app.cell
def _(mo):
    mo.image("pages/public/logo.png")
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
    return (resp,)


@app.cell
def _(client_id, clients_dashboard_modif):
    # Afficher les informations du client
    client_info = clients_dashboard_modif[clients_dashboard_modif["client_id"] == client_id]  # noqa: F841  # pyright: ignore[reportUnusedVariable]

    colonnes_a_afficher = [  # noqa: F841  # pyright: ignore[reportUnusedVariable]
        "AGE",
        "NAME_FAMILY_STATUS_Married",
        "CNT_CHILDREN",
        "CNT_FAM_MEMBERS",
        "AMT_INCOME_TOTAL",
        "YEARS_EMPLOYED",
        "FLAG_OWN_REALTY",
        "NAME_INCOME_TYPE_Working",
    ]
    return


@app.cell
def _(go, mo, resp):
    if resp is not None:
        try:
            resp.raise_for_status()
            prediction_data = resp.json()

            client_id = prediction_data["client_id"]
            prob_good = prediction_data["probability_good_customer"]
            prob_bad = prediction_data["probability_bad_customer"]
            result = prediction_data["result"]

            reponse_credit = "Accordé" if prob_good > prob_bad else "Refusé"

            text_predictions = mo.md(f"""
            ### Résultats de la prédiction pour le client {client_id}

            - Probabilité de bon client: {prob_good:.2%}
            - Probabilité de mauvais client: {prob_bad:.2%}
            - Résultat: {result}
            """)

            _fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=prob_good,
                    number={"valueformat": ".0%", "font": {"size": 28, "color": "#333"}},
                    gauge={
                        "axis": {"range": [0, 1], "tickwidth": 0, "tickcolor": "gray"},
                        "bar": {"color": "#29348D", "thickness": 0.25},  # couleur de l'aiguille
                        "bgcolor": "white",
                        "borderwidth": 1,
                        "steps": [
                            {"range": [0, 0.4], "color": "#DE0104"},  # rouge pour risque élevé
                            {"range": [0.4, 0.6], "color": "#FDC700"},  # orange moyen
                            {"range": [0.6, 1], "color": "#009937"},  # vert pour crédit accordé
                        ],
                        "threshold": {"line": {"color": "black", "width": 3}, "thickness": 0.75, "value": 0.5},
                    },
                    domain={"x": [0, 1], "y": [0, 1]},
                )
            )

            # Annotation seuil
            _fig.add_annotation(
                x=0.5,
                y=1.05,
                text="Seuil de validation (0.5)",
                showarrow=False,
                font={"size": 14, "color": "black"},
                xanchor="center",
            )

            # Annotation résultat
            _fig.add_annotation(
                x=0.5,
                y=-0.1,
                text=f"<b>Décision : {reponse_credit}</b>",
                showarrow=False,
                font={"size": 20, "color": "#2E86AB" if reponse_credit == "Accordé" else "#F44336"},
                xanchor="center",
            )

            _fig.update_layout(
                autosize=False,
                width=450,
                height=350,
                margin={"l": 30, "r": 30, "t": 40, "b": 40},
                paper_bgcolor="white",
                font={"color": "black", "family": "Arial"},
            )

            fig = mo.ui.plotly(_fig)

        except Exception as e:  # noqa: BLE001
            print(f"Erreur lors du traitement de la réponse : {e}")
    else:
        print("Erreur : La variable 'resp' n'est pas définie ou est None.")
    return client_id, fig, text_predictions  # pyright: ignore[reportPossiblyUnboundVariable]


@app.cell
def _(fig, mo, text_predictions):
    mo.hstack([text_predictions, fig])
    return


@app.cell
def _(mo):
    mo.sidebar([
        mo.md("# marimo"),
        mo.nav_menu(
            {
                "#home": f"{mo.icon('lucide:home')} Home",
                "#about": f"{mo.icon('lucide:user')} About",
                "#contact": f"{mo.icon('lucide:phone')} Contact",
                "Links": {
                    "https://twitter.com/marimo_io": "Twitter",
                    "https://github.com/marimo-team/marimo": "GitHub",
                },
            },
            orientation="vertical",
        ),
    ])
    return


@app.cell
def _(client_id, customers_df, mo):
    # Affichage du titre et de l'introduction
    mo.md("# ➤ Caractéristiques du client")
    mo.md(
        "Cette section vous permet de visualiser les caractéristiques d'un client et de les comparer à l'ensemble des clients."
    )

    # Sidebar : Marimo ne gère pas de sidebar, mais vous pouvez afficher un message en haut
    mo.md("**Naviguez dans les sections du dashboard.**")

    mo.md(f"### ➡️ L'ID client que vous avez sélectionné est : {client_id}")
    mo.md("Vous pouvez choisir un nouveau client en le sélectionnant dans l'onglet Informations Client.")

    mo.md("### ➡️ Visualisation d'une caractéristique du client par rapport aux autres clients")

    # Sélecteur pour choisir la caractéristique à visualiser
    feature_to_plot = mo.ui.dropdown(
        options=list(customers_df.columns), label="Choisissez une caractéristique à visualiser"
    )
    feature_to_plot  # pyright: ignore[reportUnusedExpression]
    return (feature_to_plot,)


@app.cell
def _(client_id, client_value, customers_df, feature_to_plot, mo, np, pd, px):
    view = None

    if pd.isna(client_value):
        view = mo.md(
            f"⚠️ La caractéristique '{feature_to_plot.value}' est manquante pour le client {client_id}. "  # pyright: ignore[reportImplicitStringConcatenation]
            "Veuillez sélectionner une autre caractéristique."
        )
    else:
        _filtered_feature_values = customers_df[feature_to_plot.value].dropna()
        _hist_values, _ = np.histogram(_filtered_feature_values, bins="auto")
        _max_y_value = _hist_values.max()

        _fig = px.histogram(
            customers_df,
            x=feature_to_plot.value,
            title=f"Distribution de {feature_to_plot.value}",
        )
        _fig.add_vline(x=client_value, line_width=3, line_dash="dash", line_color="red")
        _fig.add_annotation(
            x=client_value,
            y=_max_y_value,
            text=f"<b>Client : {client_id}</b>",
            showarrow=False,
            yshift=10,
            font={"size": 14, "color": "black"},
            xanchor="center",
        )
        view = mo.ui.plotly(_fig)

    view  # pyright: ignore[reportUnusedExpression]
    return


@app.cell
def _(client_id, customers_df, feature_to_plot, mo, np, pd, px):
    # Vérifier si la valeur pour le client est NaN
    client_value = customers_df.loc[client_id, feature_to_plot.value]

    if pd.isna(client_value):
        mo.md(
            f"⚠️ La caractéristique '{feature_to_plot.value}' est manquante pour le client {client_id}. "  # pyright: ignore[reportImplicitStringConcatenation]
            "Veuillez sélectionner une autre caractéristique."
        )

    else:
        filtered_feature_values = customers_df[feature_to_plot.value].dropna()
        hist_values, _ = np.histogram(filtered_feature_values, bins="auto")
        max_y_value = hist_values.max()

        _fig = px.histogram(customers_df, x=feature_to_plot.value, title=f"Distribution de {feature_to_plot.value}")
        _fig.add_vline(x=client_value, line_width=3, line_dash="dash", line_color="red")
        _fig.add_annotation(
            x=client_value,
            y=max_y_value,
            text=f"<b>Client :  {client_id}</b>",
            showarrow=False,
            yshift=10,
            font={"size": 14, "color": "black"},
            xanchor="center",
        )
        _fig = mo.ui.plotly(_fig)
        _fig  # pyright: ignore[reportUnusedExpression]
    return (client_value,)


@app.cell
def _(customers_df, mo):
    # 2. Analyse bi-variée entre deux caractéristiques sélectionnées
    mo.md("### ➡️ Visualisation croisée de 2 caractéristiques et mise en évidence de la probabilité de défaut")

    feature_x = mo.ui.dropdown(options=list(customers_df.columns), label="Choisissez la première caractéristique")
    feature_y = mo.ui.dropdown(options=list(customers_df.columns), label="Choisissez la seconde caractéristique")
    return feature_x, feature_y


@app.cell
def _(client_id, customers_df, feature_x, feature_y, mo, np, plt):
    mo.md(
        f"**Croisement des variables {feature_x.value} et {feature_y.value} en fonction de la probabilité de défaut des clients**"
    )

    client_x_value = customers_df.loc[customers_df["client_id"] == client_id, feature_x.value].to_numpy()[0]
    client_y_value = customers_df.loc[customers_df["client_id"] == client_id, feature_y.value].to_numpy()[0]

    _fig, _ax = plt.subplots()
    _scatter = _ax.scatter(
        customers_df[feature_x.value], customers_df[feature_y.value], c=customers_df["proba_defaut"], cmap="viridis"
    )

    if np.isnan(client_x_value) or np.isnan(client_y_value):
        mo.md(
            f"⚠️ Les données pour le client {client_id} sont manquantes pour au moins une des caractéristiques sélectionnées."
        )
    else:
        _ax.scatter(client_x_value, client_y_value, color="red", s=100, label=f"Client {client_id}", edgecolor="black")

    cbar = plt.colorbar(_scatter, ax=_ax, label="Probabilité de défaut de paiement (seuil=0.5)")
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label("Probabilité de défaut de paiement (seuil=0.5)", fontsize=8)
    _ax.set_xlabel(f"Variable {feature_x.value}", fontsize=8)
    _ax.set_ylabel(f"Variable {feature_y.value}", fontsize=8)
    _ax.tick_params(axis="both", which="major", labelsize=6)
    _ax.legend(fontsize=8)

    _fig  # Marimo affiche la figure matplotlib si c'est la dernière expression de la cellule
    return


if __name__ == "__main__":
    app.run()
