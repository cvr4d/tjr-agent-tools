@echo off
setlocal
chcp 65001 >nul

REM --- Check venv ---
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found.
    echo Please run install.bat first.
    echo.
    pause
    exit /b 1
)

REM --- Run GUI ---
start "" "venv\Scripts\pythonw.exe" gui.py
