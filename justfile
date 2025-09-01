set dotenv-load

PORT := env("PORT", "7860")
ARGS_TEST := env("_UV_RUN_ARGS_TEST", "")
ARGS_SERVE := env("_UV_RUN_ARGS_SERVE", "")

# Variables
IMAGE_NAME := "credit-scoring-api"

# Default target: show all commands
@_:
    just --list

# try app locally
[group('docker-tools')]
demo:
    docker build --network=host -t {{IMAGE_NAME}} .
    docker run -it --rm -p {{PORT}}:{{PORT}} {{IMAGE_NAME}}

# Developp app locally
[group('run')]
start-api:
    uv run uvicorn app.main:app --port 7860 --reload

# Run tests
[group('qa')]
test *args:
    uv run {{ ARGS_TEST }} -m pytest {{ args }}

_cov *args:
    uv run -m coverage {{ args }}

# Run tests and measure coverage
[group('qa')]
@cov:
    just _cov erase
    just _cov run -m pytest tests
    # Ensure ASGI entrypoint is importable.
    # You can also use coverage to run your CLI entrypoints.
    just _cov run -m app.asgi
    just _cov combine
    just _cov report
    just _cov html

# Run linters
[group('qa')]
lint:
    uvx ruff check
    uvx ruff format

# Check types
[group('qa')]
typing:
    uvx basedpyright app

# Perform all checks
[group('qa')]
check-all: lint cov typing

# Update dependencies
[group('lifecycle')]
update:
    uv sync --upgrade

# Ensure project virtualenv is up to date
[group('lifecycle')]
install:
    uv sync

# Remove temporary files
[group('lifecycle')]
clean:
    rm -rf .venv .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov
    find . -type d -name "__pycache__" -exec rm -r {} +

# Recreate project virtualenv from nothing
[group('lifecycle')]
fresh: clean install
