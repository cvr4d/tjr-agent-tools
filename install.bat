@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ============================================
echo   TJR Agent Tools - Installer
echo ============================================
echo.

REM --- Check Python ---
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found in PATH.
    echo.
    echo Please install Python 3.10+ from:
    echo   https://www.python.org/downloads/
    echo.
    echo During installation, CHECK the box:
    echo   [X] Add Python to PATH
    echo.
    pause
    exit /b 1
)

echo [OK] Python found:
python --version
echo.

REM --- Check ffmpeg ---
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] ffmpeg not found in PATH.
    echo.
    echo Some tools (sub.py, frame.py) will NOT work without it.
    echo Download from: https://www.gyan.dev/ffmpeg/builds/
    echo Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH.
    echo.
) else (
    echo [OK] ffmpeg found.
    ffmpeg -version 2>nul | findstr /r "^ffmpeg" 
    echo.
)

REM --- Create virtual environment ---
if not exist "venv" (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [OK] Virtual environment created.
    echo.
) else (
    echo [INFO] Virtual environment already exists. Skipping.
    echo.
)

REM --- Install requirements ---
echo [INFO] Installing Python packages...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install packages.
    pause
    exit /b 1
)
echo [OK] Packages installed.
echo.

REM --- Check yt-dlp ---
where yt-dlp >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] yt-dlp not found.
    echo Install it with:
    echo   pip install yt-dlp
    echo.
)

REM --- Setup subtitles folder ---
if "%TJR_SUBTITLES%"=="" (
    echo [INFO] TJR_SUBTITLES environment variable is not set.
    echo.
    set /p SUBDIR="Enter your subtitles folder path [C:\TJR_SUBTITLES]: "
    if "!SUBDIR!"=="" set SUBDIR=C:\TJR_SUBTITLES

    if not exist "!SUBDIR!" (
        echo [INFO] Creating folder: !SUBDIR!
        mkdir "!SUBDIR!"
    )

    echo [INFO] Setting TJR_SUBTITLES environment variable (user-level)...
    setx TJR_SUBTITLES "!SUBDIR!" >nul
    set TJR_SUBTITLES=!SUBDIR!
    echo [OK] TJR_SUBTITLES = !SUBDIR!
    echo.
) else (
    echo [OK] TJR_SUBTITLES already set: %TJR_SUBTITLES%
    echo.
)

echo ============================================
echo   Setup complete!
echo ============================================
echo.
echo Next steps:
echo   1. Download subtitles (see README.md)
echo   2. Run tools with:
echo        run.bat context "your phrase"
echo        run.bat fuzzy   "your frase"
echo        run.bat sub     video.mp4 5
echo        run.bat frame   video.mp4
echo.
pause
