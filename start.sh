#!/usr/bin/env bash
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
cd "$HERE"

PY=${PY:-python3}

# ── First-time setup ─────────────────────────────────────────────────────────
if [ ! -d ".venv" ]; then
  echo "First run detected — setting up environment..."

  if ! command -v "$PY" >/dev/null 2>&1; then
    echo "Error: Python not found (tried: $PY). Install Python 3 and retry."
    exit 1
  fi

  echo "Creating virtualenv with $PY..."
  $PY -m venv .venv

  echo "Installing dependencies..."
  . .venv/bin/activate
  pip install --upgrade pip wheel --quiet

  if [ -f requirements.txt ]; then
    pip install -r requirements.txt --quiet
  fi

  echo "Setup complete."
  echo
  echo "Note (Debian/Ubuntu): if the app fails to open, run:"
  echo "  sudo apt install python3-tk"
  echo
fi

# ── Launch ────────────────────────────────────────────────────────────────────
. .venv/bin/activate
exec python python/main.py
