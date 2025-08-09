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
short_description: API and interactive dashboard to predict credit default risk.
thumbnail: https://cdn-uploads.huggingface.co/production/uploads/6891c75202359d4e3846cbec/uMnppPBtSc7waPZhjrTMc.png
---

# 🏦 Implementer Model Scoring API

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
- **Marimo Dashboard**: https://laguill-implementer-model-scoring.hf.space/dashboard

---

## 🛠 Tech Stack

- [FastAPI](https://fastapi.tiangolo.com/) — API backend.
- [Marimo](https://marimo.io/) — interactive dashboard.
- [LightGBM](https://lightgbm.readthedocs.io/) — machine learning model.
- [SHAP](https://shap.readthedocs.io/) & [Plotly](https://plotly.com/) — model explainability.
- [Hugging Face Spaces](https://huggingface.co/spaces) — deployment with Docker.
- [`justfile`](https://github.com/casey/just) — command automation for development and maintenance.

---

## 📂 Project Structure

├── app/ # API routes and business logic
│ ├── api.py
│ └── init.py
├── model/ # Model and preprocessing artifacts
│ ├── Best_LGBM_Model.pkl
│ ├── encoders.pkl
│ ├── customers_data.csv
│ └── model_features.pkl
├── pages/ # Marimo dashboard
│ ├── dashboard.py
│ └── marimo/
├── tests/ # Unit tests
├── main.py # FastAPI + dashboard entrypoint
├── Dockerfile # Docker config for HF Spaces
├── pyproject.toml # Dependencies
├── uv.lock # uv lockfile for reproducibility
├── justfile # Task runner for common commands
├── development.md # Local development instructions
└── .github/workflows/ # CI/CD to sync with HF Space
