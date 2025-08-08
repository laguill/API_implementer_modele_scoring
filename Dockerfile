# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN useradd -m -u 1000 user
ENV PATH="/home/user/.local/bin:$PATH"
ENV UV_SYSTEM_PYTHON=1
ENV UV_LINK_MODE=copy
ENV UV_COMPILE_BYTECODE=1

WORKDIR /app

COPY --chown=user pyproject.toml uv.lock /app/
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
COPY --chown=user . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# User rights
RUN chown -R user /app
USER user

# Ports exposés (7860 = API)
EXPOSE 7860

# Reset the entrypoint, don't invoke `uv`
ENTRYPOINT []

# Start the 2 servers : FastAPI (backend)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
