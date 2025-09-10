import marimo


__generated_with = "0.15.2"
app = marimo.App()


@app.cell
def _():
    import base64
    import logging

    from pathlib import Path

    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    import requests

    from requests.exceptions import RequestException

    import pages.functions as fc

    return Path, fc, go, mo, pd, px


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""# Prêt à dépenser -- Accord de prêt""")
    return


@app.cell
def _(mo):
    mo.image("pages/public/logo.png")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
        Un outil de “scoring crédit” a récemment été mis en place.

        Ce dashboard interactif vous permet de:

        - visualiser les informations et les caractéristiques d'un client,
        - prédire sa probabilité de défaut de paiement
        - savoir si son crédit est accepté au vu de cette probabilité.

        Il vous donnera tous les éléments nécessaires pour expliquer de façon la plus transparente possible aux clients les décisions d’octroi de crédit.
    """  # noqa: RUF001
    ).callout(kind="info")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Informations clients""")
    return


@app.cell
def _(Path, pd):
    # charge les données du fichier csv
    MODELS_DIR = Path("models")

    CUSTOMERS_PATH = MODELS_DIR / "customers_data.csv"

    customers_df = pd.read_csv(
        CUSTOMERS_PATH,
        index_col="SK_ID_CURR",
    )

    customers_df["AGE"] = round(customers_df["DAYS_BIRTH"] / -365)
    customers_df["YEARS_EMPLOYED"] = round(customers_df["DAYS_EMPLOYED"] / -365)
    customers_df = customers_df.drop(["DAYS_BIRTH", "DAYS_EMPLOYED"], axis=1)
    return (customers_df,)


@app.cell
def _(customers_df, mo):
    client_dropdown = mo.ui.dropdown(
        options=customers_df.index[:10],
        label="Sélectionner un client",
    )
    client_dropdown  # pyright: ignore[reportUnusedExpression]
    return (client_dropdown,)


@app.cell
def _(client_dropdown):
    client_id = client_dropdown.value
    return (client_id,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Informations du client""")
    return


@app.cell
def _(mo):
    reload_btn = mo.ui.run_button(
        label="Recharger les données",
    )
    return (reload_btn,)


@app.cell
def _(mo):
    dictionnaire_descriptions = {
        "CODE_GENDER": "Genre du client",
        "AGE": "Age du client le jour de l'inscription",
        "AMT_CREDIT_x": "Montant du crédit",
        "YEARS_EMPLOYED": "Depuis combien de temps le client à un emploi",
        "FLAG_OWN_CAR": "Indique si le client possède une voiture",
        "FLAG_OWN_REALTY": "Indique si le client possède une maison ou un appartement",
        "CNT_CHILDREN": "Nombre d'enfants du client",
        "AMT_INCOME_TOTAL": "Revenu total du client",
        "AMT_ANNUITY": "Annuité de la demande précédente",
        "NAME_INCOME_TYPE": "Type de revenu du client (entrepreneur, salarié, congé maternité, etc.)",
        "DAYS_REGISTRATION": "Nombre de jours avant la demande où le client a changé son inscription",
        "DAYS_CREDIT_mean": "Nombre de jours depuis la dernière demande de crédit",
        "EXT_SOURCE_2": "Score normalisé provenant d'une source de données externe",
        "EXT_SOURCE_3": "Score normalisé provenant d'une source de données externe",
    }

    descriptions_tables = mo.ui.table(dictionnaire_descriptions)
    return (descriptions_tables,)


@app.cell
def _(client_id, customers_df, fc, mo, pd, reload_btn):
    if client_id or reload_btn.value:
        _data = fc.get_client_info(client_id)
        client_df = pd.DataFrame([_data])

        # Transformer les colonnes DAYS_BIRTH et DAYS_EMPLOYED pour qu'elles soient plus lisibles
        client_df["AGE"] = round(client_df["DAYS_BIRTH"] / -365)
        client_df["YEARS_EMPLOYED"] = round(client_df["DAYS_EMPLOYED"] / -365)
        client_df = client_df.drop(["DAYS_BIRTH", "DAYS_EMPLOYED"], axis=1)

        colonnes_a_afficher = [
            "CODE_GENDER",
            "AGE",
            "CNT_CHILDREN",
            "AMT_INCOME_TOTAL",
            "NAME_INCOME_TYPE",
            "AMT_CREDIT_x",
            "AMT_ANNUITY",
            "YEARS_EMPLOYED",
            "FLAG_OWN_CAR",
            "FLAG_OWN_REALTY",
            "EXT_SOURCE_2",
            "EXT_SOURCE_3",
            "INST_TOTAL_PAID",
            "DAYS_CREDIT_mean",
            "DAYS_REGISTRATION",
        ]

        fiche_dict = mo.ui.dictionary({
            "CODE_GENDER": mo.ui.radio(
                label="Genre (CODE_GENDER)", options=["M", "F"], value=client_df["CODE_GENDER"].iloc[0]
            ),
            "AGE": mo.ui.number(label="Âge (AGE)", value=client_df["AGE"].iloc[0], start=18, stop=100, step=1),
            "CNT_CHILDREN": mo.ui.number(
                label="Nombre d'enfants (CNT_CHILDREN)",
                value=int(client_df["CNT_CHILDREN"].iloc[0]),
                start=0,
                stop=20,
                step=1,
            ),
            "AMT_INCOME_TOTAL": mo.ui.number(
                label="Revenu total (AMT_INCOME_TOTAL)",
                value=client_df["AMT_INCOME_TOTAL"].iloc[0],
                start=0.0,
                step=1000.0,
            ),
            "NAME_INCOME_TYPE": mo.ui.dropdown(
                label="Type de revenu (NAME_INCOME_TYPE)",
                options=customers_df["NAME_INCOME_TYPE"].unique(),
                value=client_df["NAME_INCOME_TYPE"].iloc[0],
            ),
            "AMT_CREDIT_x": mo.ui.number(
                label="Montant du crédit (AMT_CREDIT_x)",
                value=client_df["AMT_CREDIT_x"].iloc[0],
                start=0.0,
                step=1000.0,
            ),
            "AMT_ANNUITY": mo.ui.number(
                label="Montant de l'annuité (AMT_ANNUITY)",
                value=client_df["AMT_ANNUITY"].iloc[0],
                start=0.0,
                step=1000.0,
            ),
            "YEARS_EMPLOYED": mo.ui.number(
                label="Années d'emploi (YEARS_EMPLOYED)", value=client_df["YEARS_EMPLOYED"].iloc[0], start=0.0, step=0.5
            ),
            "FLAG_OWN_CAR": mo.ui.radio(
                label="Possède une voiture (FLAG_OWN_CAR)", options=["Y", "N"], value=client_df["FLAG_OWN_CAR"].iloc[0]
            ),
            "FLAG_OWN_REALTY": mo.ui.radio(
                label="Possède un bien immobilier (FLAG_OWN_REALTY)",
                options=["Y", "N"],
                value=client_df["FLAG_OWN_REALTY"].iloc[0],
            ),
            "EXT_SOURCE_2": mo.ui.number(
                label="Score de solvabilité externe n°2 (EXT_SOURCE_2)",
                value=client_df["EXT_SOURCE_2"].iloc[0],
                start=0.0,
                stop=1.0,
                step=0.01,
            ),
            "EXT_SOURCE_3": mo.ui.number(
                label="Score de solvabilité externe n°3 (EXT_SOURCE_3)",
                value=client_df["EXT_SOURCE_3"].iloc[0],
                start=0.0,
                stop=1.0,
                step=0.01,
            ),
            "INST_TOTAL_PAID": mo.ui.number(
                label="Montant total payé (INST_TOTAL_PAID)",
                value=client_df["INST_TOTAL_PAID"].iloc[0],
                start=0.0,
                step=1000.0,
            ),
            "DAYS_CREDIT_mean": mo.ui.number(
                label="Moyenne des jours de crédit (DAYS_CREDIT_mean)",
                value=client_df["DAYS_CREDIT_mean"].iloc[0],
                step=1,
            ),
            "DAYS_REGISTRATION": mo.ui.number(
                label="Jours depuis l'enregistrement (DAYS_REGISTRATION)",
                value=client_df["DAYS_REGISTRATION"].iloc[0],
                step=1,
            ),
        })

        fiche_dict  # pyright: ignore[reportUnusedVariable]
    return client_df, colonnes_a_afficher, fiche_dict  # pyright: ignore[reportPossiblyUnboundVariable]


@app.cell
def _(client_id, fiche_dict, mo, reload_btn):
    # Tab 1
    tab_fetch = mo.vstack([mo.ui.table(fiche_dict.value, label=f"Données client {client_id}"), reload_btn])

    # Tab 2: Update user data (your fiche_dict UI)
    tab_update = fiche_dict.form(
        submit_button_label="Mettre à jour les informations",
        loading=False,
    )
    return tab_fetch, tab_update


@app.cell
def _(descriptions_tables, mo, tab_fetch, tab_update):
    get_tab, set_tab = mo.state("Voir les informations")
    user_tabs = mo.ui.tabs(
        {
            "Voir les informations": tab_fetch,
            "Mettre à jour": tab_update,
            "Descriptions": descriptions_tables,
        },
        value=get_tab(),
        on_change=set_tab,
    )
    user_tabs  # pyright: ignore[reportUnusedExpression]
    return


@app.cell
def _(client_id, fc, reload_btn, tab_update):
    if tab_update.value is not None:
        update_dict = tab_update.value.copy()
        update_dict["DAYS_BIRTH"] = -365 * update_dict["AGE"]
        update_dict["DAYS_EMPLOYED"] = -365 * update_dict["YEARS_EMPLOYED"]
        # Optionally remove the derived columns if needed
        del update_dict["AGE"]
        del update_dict["YEARS_EMPLOYED"]
        fc.update_client_info(client_id, update_dict)
        reload_btn.value = True
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""## Prédiction client""")
    return


@app.cell
def _(mo):
    run_button = mo.ui.run_button(label="Faire une prédiction", full_width=True)

    run_button  # pyright: ignore[reportUnusedExpression]
    return (run_button,)


@app.cell
def _(client_id, fc, mo, run_button):
    resp = None
    if run_button.value:
        with mo.status.spinner("Prédiction en cours ..."):
            resp = fc.run_prediction(client_id)
    return (resp,)


@app.cell
def _(client_id, go, mo, resp):
    if resp:
        try:
            THRESHOLD = 0.5
            resp.raise_for_status()
            prediction_data = resp.json()
            prob_good = prediction_data["probability_good_customer"]
            reponse_credit = "Accordé" if prob_good >= THRESHOLD else "Refusé"

            # Couleurs accessibles
            colors = {
                "high_risk": "#D55E00",
                "medium_risk": "#E69F00",
                "low_risk": "#009E73",
                "bar": "#ADD8E6",
                "threshold": "black",
            }

            # Jauge accessible avec espace à droite
            _fig = go.Figure(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=prob_good,
                    number={"valueformat": ".0%", "font": {"size": 28, "color": "#000"}},
                    gauge={
                        "axis": {"range": [0, 1], "tickformat": ".0%"},
                        "bar": {"color": colors["bar"], "thickness": 0.25},
                        "bgcolor": "white",
                        "steps": [
                            {"range": [0, 0.5], "color": colors["high_risk"], "name": "Risque élevé"},
                            {"range": [0.5, 0.6], "color": colors["medium_risk"], "name": "Risque moyen"},
                            {"range": [0.6, 1], "color": colors["low_risk"], "name": "Crédit accordé"},
                        ],
                        "threshold": {"line": {"color": colors["threshold"], "width": 3}, "value": THRESHOLD},
                    },
                    domain={"x": [0, 0.7], "y": [0, 1]},  # espace à droite pour la légende
                    customdata=[f"Probabilité de remboursement: {prob_good:.0%}, Décision: {reponse_credit}"],
                )
            )

            # Annotations
            _fig.add_annotation(
                x=0.35,  # centré sur la jauge
                y=1.05,
                text=f"Seuil de validation : {THRESHOLD:.0%}",
                showarrow=False,
                font={"size": 14, "color": "black"},
                xanchor="center",
            )
            _fig.add_annotation(
                x=0.35,
                y=-0.1,
                text=f"Décision : {reponse_credit}",
                showarrow=False,
                font={"size": 18, "color": colors["low_risk"] if reponse_credit == "Accordé" else colors["high_risk"]},
                xanchor="center",
            )

            # Légende à droite
            _fig.add_annotation(
                x=0.75,  # position à droite
                y=0.5,
                text="<b>Légende :</b><br>"  # pyright: ignore[reportImplicitStringConcatenation]
                f"<span style='color:{colors['high_risk']}'>■</span> 0-50% : Risque élevé<br>"
                f"<span style='color:{colors['medium_risk']}'>■</span> 50-60% : Risque moyen<br>"
                f"<span style='color:{colors['low_risk']}'>■</span> 60-100% : Crédit accordé",
                showarrow=False,
                font={"size": 12, "color": "black"},
                xanchor="left",
                yanchor="middle",
            )

            # Mise à jour de la mise en page
            _fig.update_layout(
                title_text=f"Jauge de probabilité de remboursement pour le client {client_id}",
                title_x=0.5,
                autosize=False,
                width=600,  # plus large pour la légende
                height=350,
                margin={"l": 50, "r": 50, "t": 80, "b": 50},
                paper_bgcolor="white",
                font={"color": "black"},
                meta=f"Jauge indiquant la probabilité de remboursement: {prob_good:.0%}, décision: {reponse_credit}. Seuil de validation: {THRESHOLD:.0%}",
            )

            jauge = mo.ui.plotly(_fig).center()

        except Exception as e:  # noqa: BLE001
            print(f"Erreur lors du traitement de la réponse : {e}")
    return (jauge,)


@app.cell
def _(jauge, mo, resp):
    _output = None
    if resp:
        _output = mo.vstack([jauge], align="center", justify="center")
    _output  # pyright: ignore[reportUnusedExpression]
    return


@app.cell(hide_code=True)
def _(mo, resp):
    _output = None
    if resp:
        _output = mo.md(r"""ℹ️ Interprétation du score de solvabilité :

        Le score de solvabilité est un indicateur numérique.

        On l'utilise pour évaluer la solvabilité ou le risque d'un client à partir d'informations externes, comme des données de bureau de crédit ou d'autres bases de données financières.

        Plus le score est élevé (proche de 1), plus la probabilité de remboursement est forte.""").callout(kind="info")  # noqa: RUF001

    _output  # pyright: ignore[reportUnusedExpression]
    return


@app.cell(hide_code=True)
def _(mo, resp):
    if resp:
        mo.md(r"""### Importance des caractéristiques""")
    return


@app.cell
def _(client_id, fc, mo, pd, px, resp):
    if resp:
        local_feature_importance = fc.get_local_feature_importance(client_id)

        local_importance_df = pd.DataFrame(list(local_feature_importance.items()), columns=["feature", "importance"])
        _fig_local = px.bar(
            local_importance_df.head(10), x="feature", y="importance", title="Feature Importance Locale (Top 10)"
        )
        _fig_local.update_layout(title_text="Feature Importance Locale (Top 10)", title_x=0.5)
        _fig_local.update_traces(
            marker_color="rgb(158,202,225)", marker_line_color="rgb(8,48,107)", marker_line_width=1.5, opacity=0.6
        )
        local_plot = mo.ui.plotly(_fig_local).center()
    return (local_plot,)


@app.cell
def _(client_id, fc, mo, resp):
    if resp:
        waterfall = mo.image(fc.get_shap_summary_plot(client_id))
    return (waterfall,)


@app.cell
def _(fc, mo, pd, px, resp):
    if resp:
        global_feature_importance = fc.get_global_feature_importance()

        global_importance_df = pd.DataFrame(global_feature_importance.items(), columns=["feature", "importance"])
        global_importance_df["importance"] = global_importance_df["importance"].astype(float)
        fig_global = px.bar(
            global_importance_df.head(10), x="feature", y="importance", title="Feature Importance Globale"
        )
        fig_global.update_layout(title_text="Feature Importance Globale", title_x=0.5)
        fig_global.update_traces(
            marker_color="rgb(123,204,196)", marker_line_color="rgb(4,77,51)", marker_line_width=1.5, opacity=0.6
        )
        global_plot = mo.ui.plotly(fig_global).center()
    return (global_plot,)


@app.cell(hide_code=True)
def _(descriptions_tables, global_plot, local_plot, mo, resp, waterfall):
    tabs = None
    if resp:
        tab_content = {
            "Importance Locale": local_plot,
            "Correlation": waterfall,
            "Importance Globale": global_plot,
            "Descriptions": descriptions_tables,
        }
        tabs = mo.ui.tabs(tab_content)
    tabs  # Affiche les tabs  # pyright: ignore[reportUnusedExpression]
    return (tabs,)


@app.cell(hide_code=True)
def _(mo, resp, tabs):
    _output = None
    if resp:
        with mo.status.spinner("Chargement des graphiques ..."):
            if tabs.value == "Importance Locale":
                _output = mo.md(
                    """
                    Le graphique ci-dessus montre l'importance des différentes caractéristiques **locales**.

                    Chaque barre représente une caractéristique avec son niveau d'importance.
                    """
                )
            elif tabs.value == "Correlation":
                _output = mo.md(
                    """
                    Ce graphique montre comment chaque variable influence la prédiction du modèle pour ce client :

            - En rouge : les caractéristiques qui augmentent la probabilité de défaut.
            - En bleu : celles qui la diminuent.
                    """
                )
            elif tabs.value == "Importance Globale":
                _output = mo.md(
                    """
                    Le graphique ci-dessus montre l'importance des différentes caractéristiques **globales**.

                    Chaque barre représente une caractéristique avec son niveau d'importance.
                    """
                )
    _output  # pyright: ignore[reportUnusedExpression]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        r"""
    ## Caractéristiques client

    Cette section vous permet de visualiser les caractéristiques d'un client et de les comparer à l'ensemble des clients.
    """
    )
    return


@app.cell
def _(colonnes_a_afficher, mo, resp):
    feature_to_plot = None
    if resp:
        # Sélecteur pour choisir la caractéristique à visualiser
        feature_to_plot = mo.ui.dropdown(
            options=list(colonnes_a_afficher), label="Choisissez une caractéristique à visualiser"
        )
    feature_to_plot  # pyright: ignore[reportUnusedExpression]
    return (feature_to_plot,)


@app.cell
def _(client_df, client_id, customers_df, feature_to_plot, mo, pd, px):
    _view = None

    if client_id and feature_to_plot.value:
        with mo.status.spinner("Chargement du graphique ..."):
            feature = feature_to_plot.value

            if pd.api.types.is_numeric_dtype(customers_df[feature]):
                # Cas numérique
                _fig = px.histogram(customers_df, x=feature, title=f"Distribution de {feature}")
                _fig.add_vline(
                    x=float(client_df[feature].iloc[0]),
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Client",
                )
            else:
                # Cas catégoriel
                _fig = px.histogram(customers_df, x=feature, title=f"Distribution de {feature}")
                client_value = client_df[feature].iloc[0]
                _fig.add_annotation(
                    x=client_value,
                    y=customers_df[feature].value_counts()[client_value],
                    text="Client",
                    showarrow=True,
                    arrowhead=2,
                    arrowcolor="red",
                    font={"color": "red", "size": 12},
                )

            _fig.update_layout(title_text=f"Distribution de {feature}", title_x=0.5)
            _fig.update_traces(
                marker_color="rgb(246,207,113)", marker_line_color="rgb(205,102,0)", marker_line_width=1.5, opacity=0.6
            )

            _view = mo.ui.plotly(_fig)
    _view  # pyright: ignore[reportUnusedExpression]
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""### Analyse bi-variée entre deux caractéristiques""")
    return


@app.cell
def _(mo):
    combinations_interessantes = {
        "Revenu vs Crédit": ("AMT_INCOME_TOTAL", "AMT_CREDIT_x"),
        "Revenu vs Annuité": ("AMT_INCOME_TOTAL", "AMT_ANNUITY"),
        "Crédit vs Annuité": ("AMT_CREDIT_x", "AMT_ANNUITY"),
        "Âge vs Crédit": ("AGE", "AMT_CREDIT_x"),
        "Âge vs Revenu": ("AGE", "AMT_INCOME_TOTAL"),
        "Ancienneté emploi vs Revenu": ("YEARS_EMPLOYED", "AMT_INCOME_TOTAL"),
        "Ancienneté emploi vs Crédit": ("YEARS_EMPLOYED", "AMT_CREDIT_x"),
        "Score externe 2 vs Score externe 3": ("EXT_SOURCE_2", "EXT_SOURCE_3"),
        "Dernier crédit vs Montant crédit": ("DAYS_CREDIT_mean", "AMT_CREDIT_x"),
        "Nombre d’enfants vs Revenu": ("CNT_CHILDREN", "AMT_INCOME_TOTAL"),  # noqa: RUF001
    }

    selected_label = mo.ui.dropdown(
        options=combinations_interessantes,
        label="Choisissez une analyse :",
    )

    mo.hstack([selected_label])
    return (selected_label,)


@app.cell
def _(client_df, customers_df, mo, px, selected_label):
    bi_varie_plot = None
    feature1, feature2 = selected_label.value

    if feature1 and feature2:
        with mo.status.spinner("Chargement du graphique ..."):
            # Graphe avec l'ensemble des clients
            _fig_bivariate = px.scatter(
                customers_df, x=feature1, y=feature2, title=f"Analyse bi-variée entre {feature1} et {feature2}"
            )
            _fig_bivariate.update_layout(title_text=f"Analyse bi-variée entre {feature1} et {feature2}", title_x=0.5)
            _fig_bivariate.update_traces(
                marker_color="rgb(229,152,102)", marker_line_color="rgb(174,49,0)", marker_line_width=1.5, opacity=0.6
            )

            if not client_df.empty:
                _fig_bivariate.add_scatter(
                    x=client_df[feature1],
                    y=client_df[feature2],
                    mode="markers+text",
                    text="Client",
                    textposition="top center",
                    marker={"color": "red", "size": 14, "line": {"color": "rgb(205,102,0)", "width": 1.5}},
                    name="Client actuel",
                )

            _text_explaination = mo.md(
                f"""Le graphique ci-dessus montre la relation entre **{feature1}** et **{feature2}**
                pour l'ensemble des clients.
                🔴 Le point rouge indique la position du client sélectionné."""
            )

            bi_varie_plot = mo.vstack([mo.ui.plotly(_fig_bivariate), _text_explaination])
    bi_varie_plot  # pyright: ignore[reportUnusedExpression]
    return


if __name__ == "__main__":
    app.run()
