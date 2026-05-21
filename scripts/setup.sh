#!/usr/bin/env bash
# scripts/setup.sh
# TaskFlow AI — developer environment setup
# Usage: bash scripts/setup.sh

set -e   # exit immediately on any error

echo "TaskFlow AI — Developer Setup"
echo "=============================="

# Check Python version
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python -m venv .venv

# Activate
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip --quiet

# Install all dependencies
echo "Installing dependencies..."
pip install -e ".[dev]" --quiet

echo ""
echo "Setup complete!"
echo "Activate with: source .venv/bin/activate"
echo "Run with:      python run.py"