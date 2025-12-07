#!/bin/bash
# IHP gm/ID Design Kit - Virtual Environment Setup
# Usage: source setup_venv.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"

echo "=========================================="
echo "IHP gm/ID Design Kit - Environment Setup"
echo "=========================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "Python version: $PYTHON_VERSION"

if [[ $(echo "$PYTHON_VERSION < 3.9" | bc -l) -eq 1 ]]; then
    echo "ERROR: Python 3.9+ required, found $PYTHON_VERSION"
    exit 1
fi

# Create virtual environment
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
else
    echo "Virtual environment already exists"
fi

# Activate
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "Installing dependencies..."
pip install -r "$SCRIPT_DIR/requirements.txt" -q

echo ""
echo "=========================================="
echo "Setup complete!"
echo "=========================================="
echo ""
echo "To activate the environment in the future:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "To verify installation:"
echo "  python examples/basic_usage.py"
echo ""
