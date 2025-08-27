FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        cmake \
        build-essential \
        gcc \
        g++ \
        curl \
        git \
        libomp-dev && \
    # clean
    apt-get autoremove -y && apt-get clean && \
    rm -rf /usr/local/src/*

# Créer un utilisateur non-root
RUN useradd -m -u 1000 appuser
ENV PATH="/home/appuser/.local/bin:$PATH"
ENV UV_SYSTEM_PYTHON=1

# Créer dossier app
WORKDIR /workspace

# Copier uniquement les fichiers de dépendances pour optimiser le cache
COPY --chown=appuser pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache  --no-dev

# Copier tout le code source + dossiers nécessaires
COPY --chown=appuser app/ ./app/
COPY --chown=appuser models/ ./models/
COPY --chown=appuser pages/ ./pages/

# Changer les droits et passer en utilisateur non-root
RUN mkdir -p ./pages/__marimo__ && \
    chown -R appuser:appuser /workspace && \
    chmod -R 755 /workspace

USER appuser

ENV PORT=7860
EXPOSE 7860

#CMD ["uv", "run", "app/main.py"]
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860"]


