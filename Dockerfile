FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Créer un utilisateur non-root
RUN useradd -m -u 1000 user

WORKDIR /app

# Étape 1 : installation des dépendances (optimise le cache)
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# Étape 2 : copier le reste du projet et installer le package local
COPY . .
RUN uv sync --locked --no-dev

# Ajouter le venv au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Changer les droits et passer en utilisateur non-root
RUN chown -R user /app
USER user

EXPOSE 7860

CMD ["uv", "run", "main.py"]
