@echo off
setlocal EnableDelayedExpansion
title Claisum Installer

echo.
echo  ==========================================
echo   Claisum Installer for Windows
echo   https://github.com/claisum/Claisum.py
echo  ==========================================
echo.

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [ERROR] Python was not found on your system.
    echo.
    echo  Please install Python 3.12 or higher from:
    echo  https://www.python.org/downloads/
    echo.
    echo  Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set PYTHON_VERSION=%%v
echo  Python found: %PYTHON_VERSION%
echo.

:: Install directly from GitHub using pip (no ZIP download or extraction needed)
echo  Installing Claisum from GitHub...
pip install "https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip" --quiet
if %errorlevel% neq 0 (
    echo.
    echo  [ERROR] Installation failed.
    echo.
    echo  Try installing manually:
    echo    pip install https://github.com/claisum/Claisum.py/archive/refs/heads/main.zip
    echo.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo   Claisum installed successfully!
echo  ==========================================
echo.
echo  Get started:
echo    claisum --help
echo    claisum discord themes list
echo    claisum discord plugins available
echo.
pause
