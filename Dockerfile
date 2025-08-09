FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Créer un utilisateur non-root
RUN useradd -m -u 1000 user

WORKDIR /app

# Copier uniquement les fichiers de dépendances pour optimiser le cache
COPY --chown=user pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev

# Copier tout le code source + dossiers nécessaires
# Copier tout le code source + dossiers nécessaires
COPY --chown=user . /app/

# Ajouter le venv au PATH
ENV PATH="/app/.venv/bin:$PATH"

# Changer les droits et passer en utilisateur non-root
RUN chown -R user /app
USER user

EXPOSE 7860

CMD ["uv", "run", "main.py"]
