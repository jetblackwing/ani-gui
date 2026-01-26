#!/bin/bash
# setup-venv.sh - Create and configure virtual environment for ani-gui

set -e

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "✓ Virtual environment setup complete!"
echo ""
echo "To activate the environment, run:"
echo "  source venv/bin/activate"
echo ""
echo "To run ani-gui, execute:"
echo "  python3 run-app.py"
echo ""
echo "To deactivate when done:"
echo "  deactivate"
