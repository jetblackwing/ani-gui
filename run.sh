#!/bin/bash
# run.sh - Simple launcher script for ani-gui
# Copyright 2024 Amal J Krishnan <amaljk80@gmail.com> (@jetblackwing)
# This script automatically sets up and runs ani-gui

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

echo "🎬 Ani-GUI Launcher"
echo "─────────────────────"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Virtual environment not found. Setting up..."
    bash setup-venv.sh
fi

echo ""
echo "✓ Activating virtual environment..."
source venv/bin/activate

echo "✓ Starting Ani-GUI..."
python3 run-app.py
