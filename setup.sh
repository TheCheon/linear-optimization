#!/usr/bin/env bash
set -euo pipefail

# Lightweight project setup for Linux/macOS
# - creates a virtualenv in .venv
# - installs pip requirements
# - prints next steps to activate the venv

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

PY=${PY:-python3}
if ! command -v "$PY" >/dev/null 2>&1; then
  echo "Error: Python not found (tried: $PY). Install Python 3 and retry."
  exit 1
fi

echo "Creating virtualenv with $PY..."
$PY -m venv .venv

echo "Installing wheel and pip latest..."
. .venv/bin/activate
pip install --upgrade pip wheel

if [ -f requirements.txt ]; then
  echo "Installing requirements.txt..."
  pip install -r requirements.txt
else
  echo "No requirements.txt found — skipping pip install"
fi

echo
echo "Setup complete. To activate the venv run:"
echo "  source .venv/bin/activate"
echo
echo "Notes:"
echo " - On Debian/Ubuntu you may need 'sudo apt install python3-tk' to enable Tkinter GUI support."
echo " - On macOS the system Python often includes Tk; if not, install Python from python.org or Homebrew."

exit 0
