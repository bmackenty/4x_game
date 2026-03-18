"""
run.py — Single-command launcher for the 4X game.

Usage:
    python run.py

What it does:
    1. Starts the FastAPI backend (uvicorn) on localhost:8765
    2. Waits 1.5 seconds for the server to boot
    3. Opens the game in the system's default web browser
    4. Blocks until you press Ctrl+C, then shuts down cleanly

Requirements:
    pip install fastapi "uvicorn[standard]"
"""

import subprocess
import sys
import time
import webbrowser
import os

# Port the game server will listen on
PORT = 8765

# Project root — same directory as this file
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    print(f"[4X Game] Starting server at http://localhost:{PORT} ...")

    # Start uvicorn as a subprocess.
    # --reload enables auto-restart on source file changes (developer mode).
    # The working directory is the project root so that relative paths inside
    # game.py (e.g. the saves/ directory) resolve correctly.
    proc = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host", "127.0.0.1",
            "--port", str(PORT),
            "--reload",
            "--reload-include", "*.json",
        ],
        cwd=PROJECT_ROOT,
    )

    # Give uvicorn time to bind the port before we open the browser
    time.sleep(1.5)

    url = f"http://localhost:{PORT}"
    print(f"[4X Game] Opening browser at {url}")
    webbrowser.open(url)

    print("[4X Game] Server running. Press Ctrl+C to stop.")
    try:
        proc.wait()
    except KeyboardInterrupt:
        print("\n[4X Game] Shutting down...")
        proc.terminate()
        proc.wait()
        print("[4X Game] Server stopped.")


if __name__ == "__main__":
    main()
