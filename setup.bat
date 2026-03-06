@echo off
REM Lightweight project setup for Windows (cmd)
REM - creates a virtualenv in .venv
REM - installs pip requirements

SET PY=python
%PY% -m venv .venv
if ERRORLEVEL 1 (
  echo Failed to create virtualenv. Make sure Python is on PATH.
  exit /b 1
)

call .venv\Scripts\activate
python -m pip install --upgrade pip wheel
IF EXIST requirements.txt (
  pip install -r requirements.txt
) ELSE (
  echo No requirements.txt found — skipping pip install
)

echo.
echo Setup complete. Activate the venv with:
echo    .venv\Scripts\activate
echo.
echo Note: If Tkinter is missing, install "python3tk" or use the official Python installer.

exit /b 0
