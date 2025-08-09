# Variables
PORT := "7860"
IMAGE_NAME := "credit-scoring-api"

# Default target: show all commands
@_:
    just --list

# try app locally
[group('docker-tools')]
demo:
    docker build --network=host -t {{IMAGE_NAME}} .
    docker run -it --rm -p {{PORT}}:{{PORT}} {{IMAGE_NAME}}

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
check-all: lint typing

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
