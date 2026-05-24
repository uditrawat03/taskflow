#!/usr/bin/env bash
# scripts/setup.sh — Developer environment setup.
# Usage: bash scripts/setup.sh

set -e

echo "TaskFlow AI — Developer Setup"
echo "=============================="

python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python: $python_version"

# Check for uv (faster) or fall back to pip
if command -v uv &>/dev/null; then
    echo "Using uv..."
    uv venv
    uv pip install -e ".[dev]"
else
    echo "uv not found — using pip..."
    python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip --quiet
    pip install -e ".[dev]" --quiet
fi

# Copy .env if not present
if [ ! -f .env ]; then
    cp .env.example .env
    echo ".env created from template — edit it with your details."
fi

echo ""
echo "Setup complete!"
echo "Activate with: source .venv/bin/activate"
echo "Run with:      python run.py"