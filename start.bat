@echo off
setlocal

cd /d "%~dp0"

REM ── First-time setup ────────────────────────────────────────────────────────
if not exist ".venv\" (
  echo First run detected -- setting up environment...

  python --version >nul 2>&1
  if ERRORLEVEL 1 (
    echo Python not found. Attempting automatic install...

    where winget >nul 2>&1
    if ERRORLEVEL 1 (
      echo winget not found. Attempting PowerShell download+install (may require admin)...
      rem Use a temporary PowerShell script to avoid cmd parentheses/quoting issues
      set "_ps=%TEMP%\python_install.ps1"
      >"%_ps%" echo $url = 'https://www.python.org/ftp/python/3.12.2/python-3.12.2-amd64.exe'
      >>"%_ps%" echo $out = [IO.Path]::Combine($env:TEMP,'python-installer.exe')
      >>"%_ps%" echo Invoke-WebRequest -Uri $url -OutFile $out -UseBasicParsing
      >>"%_ps%" echo Start-Process -FilePath $out -ArgumentList '/quiet','InstallAllUsers=1','PrependPath=1' -Wait
      >>"%_ps%" echo exit 0
      powershell -NoProfile -ExecutionPolicy Bypass -File "%_ps%"
      if ERRORLEVEL 1 (
        echo Automatic install failed. Opening browser for manual download...
        start https://www.python.org/downloads/windows/
      )
      del "%_ps%" 2>nul
    ) else (
      echo Installing Python via winget...
      winget install --id Python.Python.3 -e --silent
      if ERRORLEVEL 1 (
        echo winget install failed. Opening browser for manual download...
        start https://www.python.org/downloads/windows/
      )
    )

    REM Re-check python after attempted install
    python --version >nul 2>&1
    if ERRORLEVEL 1 (
      echo Python is still not installed. Please install Python manually and re-run this script.
      pause
      exit /b 1
    )
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
