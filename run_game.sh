#!/bin/bash

# 4X Game Launcher
echo "Starting Galactic Empire Management System..."
echo "Checking Python installation..."

if command -v python3 &> /dev/null; then
    python3 game.py
elif command -v python &> /dev/null; then
    python game.py
else
    echo "Error: Python is not installed or not in PATH"
    echo "Please install Python 3 to run this game."
    exit 1
fi