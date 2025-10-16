#!/bin/bash

# Galactic Empire Management System - UI Launcher
# Modern ASCII interface with mouse support

cd "$(dirname "$0")"

echo "🚀 Launching Galactic Empire Management System..."
echo "   Modern ASCII Interface with Mouse Support"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Setting up virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install textual rich
else
    source venv/bin/activate
fi

# Launch the interface
echo "Starting interface..."
python3 textual_interface.py

echo ""
echo "Thank you for playing Galactic Empire Management!"