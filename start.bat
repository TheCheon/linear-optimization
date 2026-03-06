@echo off
setlocal

cd /d "%~dp0"

REM ── First-time setup ────────────────────────────────────────────────────────
if not exist ".venv\" (
  echo First run detected -- setting up environment...

  python --version >nul 2>&1
  if ERRORLEVEL 1 (
    echo Error: Python not found. Install Python 3 from https://python.org and retry.
    pause
    exit /b 1
  )

  echo Creating virtualenv...
  python -m venv .venv
  if ERRORLEVEL 1 (
    echo Failed to create virtualenv.
    pause
    exit /b 1
  )

  echo Installing dependencies...
  call .venv\Scripts\activate
  python -m pip install --upgrade pip wheel --quiet
  if exist requirements.txt (
    pip install -r requirements.txt --quiet
  )

  echo.
  echo Setup complete.
  echo.
)

REM ── Launch ───────────────────────────────────────────────────────────────────
call .venv\Scripts\activate
python python\main.py
