---
title: Implementer Model Scoring API
emoji: 🏦
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: latest
pinned: true
license: mit
app_file: app/main.py
short_description: API et tableau de bord pour prédire le risque de défaut de crédit.
thumbnail: https://cdn-uploads.huggingface.co/production/uploads/6891c75202359d4e3846cbec/uMnppPBtSc7waPZhjrTMc.png
---

# 🏦 Implement Scoring Model API

![](pages/public/logo.png)

<p align="left">
  <!-- Badge CI QA (tests, lint, typing) -->
  <img src="https://github.com/laguill/API_implementer_modele_scoring/actions/workflows/qa.yml/badge.svg" alt="CI QA" />

  <img src="https://img.shields.io/github/actions/workflow/status/laguill/API_implementer_modele_scoring/hf_sync.yml?branch=main&label=HF%20Sync&logo=huggingface&style=for-the-badge" alt="HF Sync" />
</p>

Ce Hugging Face Space présente un modèle de scoring de risque de défaut de crédit construit à partir du jeu de données [Home Credit Default Risk (Kaggle)](https://www.kaggle.com/c/home-credit-default-risk/data).
L'objectif est de **prédire si un client remboursera son crédit ou fera défaut**.

Le modèle a été conçu, itéré et optimisé dans [ce notebook](https://github.com/laguill/OC-DataScientist/blob/main/P7_Implementer-model-scoring/notebooks/notebook_modelisation.py).


---

## 📊 Fonctionnalités
- **Backend FastAPI** exposant des endpoints de prédiction.
- **Documentation interactive de l'API** à `/docs` (Swagger) et `/redoc`.
- **Tableau de bord Marimo** à `/pages/dashboard` pour l'explicabilité du modèle :
  - Affiche les 15 caractéristiques les plus importantes du modèle.
  - Graphiques SHAP en cascade pour expliquer chaque prédiction.
  - Visualisations Plotly pour positionner le client parmi tous les clients.
  - Infobulles décrivant chaque caractéristique.

---

## 🚀 Live Demo

- **Application principale** : [https://laguill-implementer-model-scoring.hf.space](https://laguill-implementer-model-scoring.hf.space)
- **Documentation de l'API** : [https://laguill-implementer-model-scoring.hf.space/docs](https://laguill-implementer-model-scoring.hf.space/docs)
- **Tableau de bord Marimo** : [https://laguill-implementer-model-scoring.hf.space/pages/dashboard](https://laguill-implementer-model-scoring.hf.space/pages/dashboard)


---

## 🛠 Stack Technique
- [FastAPI](https://fastapi.tiangolo.com/) — Backend de l'API.
- [Marimo](https://marimo.io/) — Tableau de bord interactif.
- [LightGBM](https://lightgbm.readthedocs.io/) — Modèle de machine learning.
- [SHAP](https://shap.readthedocs.io/) — Explicabilité du modèle.
- [Hugging Face Spaces](https://huggingface.co/spaces) — Déploiement avec Docker.
- [Pytest](https://docs.pytest.org/en/stable/) — Tests de l'API.
- [`justfile`](https://github.com/casey/just) — Automatisation des commandes pour le développement et la maintenance.


---

## 📂 Structure du Projet
```bash
.
├── app/                   # Backend de l'API
│   ├── api/               # Routes de l'API (prédiction, healthcheck, etc.)
│   ├── asgi.py            # Point d'entrée ASGI (pour le déploiement)
│   └── main.py            # Point d'entrée de l'application FastAPI
│
├── models/                # Artefacts du modèle et du prétraitement
│   ├── Best_LGBM_Model.pkl
│   ├── encoders.pkl
│   ├── customers_data.csv
│   └── model_features.pkl
│
├── pages/                 # Tableaux de bord Marimo
│   └── dashboard.py
│
├── tests/                 # Tests unitaires
│   ├── test_main.py
│   ├── test_pages.py
│   └── test_predict.py
│
├── Dockerfile             # Configuration Docker (pour Hugging Face Spaces)
├── pyproject.toml         # Dépendances et configuration du projet
├── uv.lock                # Fichier de verrouillage pour la reproductibilité
├── justfile               # Commandes courantes de développement (build, lint, test…)
├── development.md         # Instructions pour le développement local
└── README.md              # Documentation du projet
---

## 🏃Exécution en Local

Clonez le dépôt et installez les dépendances :

```bash
git clone https://github.com/laguill/API_implementer_modele_scoring.git
cd API_implementer_modele_scoring
just install
just start-api
```

Ouvrez ensuite :

Documentation Swagger → http://127.0.0.1:7836/docs
Tableau de bord → http://127.0.0.1:7836/pages/dashboard

---

## 📡 Exemple d'Utilisation

En Python

```python
import requests

resp = requests.post(
    "http://127.0.0.1:8000/api/v1/predict",
    json={"SK_ID_CURR": 100001}
)
print(resp.json())
```

---

## ✅ License

MIT License.
N'hésitez pas à utiliser, modifier et distribuer ce projet.
