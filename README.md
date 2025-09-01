---
title: Implementer Model Scoring API
emoji: 🏦
colorFrom: blue
colorTo: indigo
sdk: docker
sdk_version: latest
pinned: true
license: mit
app_file: main.py
short_description: API and dashboard to predict credit default risk.
thumbnail: https://cdn-uploads.huggingface.co/production/uploads/6891c75202359d4e3846cbec/uMnppPBtSc7waPZhjrTMc.png
---

# 🏦 Implement Scoring Model API

![](logo.png)

<p align="left">
  <!-- Badge CI QA (tests, lint, typing) -->
  <img src="https://github.com/laguill/API_implementer_modele_scoring/actions/workflows/qa.yml/badge.svg" alt="CI QA" />

  <img src="https://img.shields.io/github/actions/workflow/status/laguill/API_implementer_modele_scoring/hf_sync.yml?branch=main&label=HF%20Sync&logo=huggingface&style=for-the-badge" alt="HF Sync" />
</p>

This Hugging Face Space demonstrates a credit default risk scoring model built from the [Home Credit Default Risk (Kaggle)](https://www.kaggle.com/c/home-credit-default-risk/data) dataset.

The goal is to **predict whether a client will repay their credit or default**.
The model was designed, iterated, and optimized in [this notebook](https://github.com/laguill/OC-DataScientist/blob/main/P7_Implementer-model-scoring/notebooks/notebook_modelisation.py).

---

## 📊 Features

- **FastAPI** backend exposing prediction endpoints.
- **Interactive API documentation** at `/docs` (Swagger) and `/redoc`.
- **Marimo dashboard** at `/dashboard` for model explainability:
  - Displays the 15 most important model features.
  - SHAP waterfall plots to explain each prediction.
  - Plotly visualizations to position the client among all customers.
  - Tooltips describing each feature.

---

## 🚀 Live Demo

- **Main App**: https://laguill-implementer-model-scoring.hf.space
- **API Docs**: https://laguill-implementer-model-scoring.hf.space/docs
- **Marimo Dashboard**: https://laguill-implementer-model-scoring.hf.space/pages/dashboard

---

## 🛠 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) — API backend.
- [Marimo](https://marimo.io/) — interactive dashboard.
- [LightGBM](https://lightgbm.readthedocs.io/) — machine learning model.
- [SHAP](https://shap.readthedocs.io/) — model explainability.
- [Hugging Face Spaces](https://huggingface.co/spaces) — deployment with Docker.
- [Pytest](https://docs.pytest.org/en/stable/) - test API
- [`justfile`](https://github.com/casey/just) — command automation for development and maintenance.

---

## 📂 Project Structure

```bash
.
├── app/                   # API backend
│   ├── api/               # API routes (prediction, healthcheck, etc.)
│   ├── asgi.py            # ASGI entrypoint (for deployment)
│   └── main.py            # FastAPI application entrypoint
│
├── models/                # Model and preprocessing artifacts
│   ├── Best_LGBM_Model.pkl
│   ├── encoders.pkl
│   ├── customers_data.csv
│   └── model_features.pkl
│
├── pages/                 # Marimo dashboards
│   └── dashboard.py
│
├── tests/                 # Unit tests
│   ├── test_main.py
│   ├── test_pages.py
│   └── test_predict.py
│
├── Dockerfile             # Docker config (for Hugging Face Spaces)
├── pyproject.toml         # Project dependencies and config
├── uv.lock                # Lockfile for reproducibility
├── justfile               # Common dev commands (build, lint, test…)
├── development.md         # Instructions for local development
└── README.md              # Project documentation
```

---

## 🏃 Run Locally

Clone the repository and install dependencies:

```bash
git clone https://github.com/laguill/API_implementer_modele_scoring.git
cd API_implementer_modele_scoring
just start-api
```

Now open:

Swagger docs → http://127.0.0.1:7836/docs

Dashboard → http://127.0.0.1:7836/pages/dashboard

---

## 📡 Usage Example

In Python

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
Feel free to use, modify, and distribute this project.
