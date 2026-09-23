@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ============================================
echo   TJR Agent Tools - Auto Installer
echo ============================================
echo.

REM ==========================================
REM 1) Check Python
REM ==========================================
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

REM ==========================================
REM 2) Check pip
REM ==========================================
python -m pip --version >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] pip not found. Installing...
    python -m ensurepip --upgrade
    echo [OK] pip installed.
    echo.
)

REM ==========================================
REM 3) Auto-install yt-dlp (global)
REM ==========================================
where yt-dlp >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] yt-dlp not found. Installing globally...
    python -m pip install --upgrade yt-dlp
    if !errorlevel! neq 0 (
        echo [WARNING] Failed to install yt-dlp. Install manually: pip install yt-dlp
    ) else (
        echo [OK] yt-dlp installed.
    )
    echo.
) else (
    echo [OK] yt-dlp already installed.
    echo.
)

REM ==========================================
REM 4) Check ffmpeg
REM ==========================================
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] ffmpeg not found in PATH.
    echo.

    REM --- Check if we can find it in C:\ffmpeg ---
    if exist "C:\ffmpeg\bin\ffmpeg.exe" (
        echo [INFO] Found ffmpeg at C:\ffmpeg\bin
        echo [INFO] Adding C:\ffmpeg\bin to PATH...
        setx PATH "%PATH%;C:\ffmpeg\bin" >nul
        set "PATH=%PATH%;C:\ffmpeg\bin"
        echo [OK] ffmpeg added to PATH.
        echo [WARNING] You may need to restart your terminal for PATH change.
        echo.
    ) else (
        echo [INFO] ffmpeg not installed. Attempting automatic download...
        echo.

        REM --- Check for curl (built into Windows 10+) ---
        where curl >nul 2>nul
        if !errorlevel! neq 0 (
            echo [ERROR] curl not found. Cannot download ffmpeg automatically.
            echo.
            echo Please install ffmpeg manually:
            echo   1. Go to https://www.gyan.dev/ffmpeg/builds/
            echo   2. Download "ffmpeg-release-essentials.zip"
            echo   3. Extract to C:\ffmpeg
            echo   4. Add C:\ffmpeg\bin to PATH
            echo.
            pause
            goto :skip_ffmpeg
        )

        echo [INFO] Downloading ffmpeg (this may take 1-2 minutes)...
        set "FFMPEG_URL=https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        set "FFMPEG_ZIP=%TEMP%\ffmpeg.zip"

        curl -L -o "!FFMPEG_ZIP!" "!FFMPEG_URL!"
        if !errorlevel! neq 0 (
            echo [ERROR] Download failed.
            echo Please install manually: https://www.gyan.dev/ffmpeg/builds/
            pause
            goto :skip_ffmpeg
        )
        echo [OK] Downloaded.
        echo.

        echo [INFO] Extracting...
        if exist "C:\ffmpeg" rmdir /s /q "C:\ffmpeg"
        mkdir "C:\ffmpeg_temp"
        tar -xf "!FFMPEG_ZIP!" -C "C:\ffmpeg_temp"
        if !errorlevel! neq 0 (
            echo [ERROR] Extraction failed.
            pause
            goto :skip_ffmpeg
        )

        REM --- Move to C:\ffmpeg ---
        for /d %%D in ("C:\ffmpeg_temp\ffmpeg-*") do (
            move "%%D" "C:\ffmpeg" >nul
            goto :moved
        )
        :moved
        rmdir /s /q "C:\ffmpeg_temp"
        del "!FFMPEG_ZIP!"

        REM --- Add to PATH ---
        echo [INFO] Adding C:\ffmpeg\bin to PATH...
        setx PATH "%PATH%;C:\ffmpeg\bin" >nul
        set "PATH=%PATH%;C:\ffmpeg\bin"
        echo [OK] ffmpeg installed and added to PATH.
        echo [WARNING] Restart your terminal for PATH to take effect.
        echo.
    )
) else (
    echo [OK] ffmpeg already installed.
    ffmpeg -version 2>nul | findstr /r "^ffmpeg"
    echo.
)

:skip_ffmpeg

REM ==========================================
REM 5) Create virtual environment
REM ==========================================
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

REM ==========================================
REM 6) Install Python packages
REM ==========================================
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

REM ==========================================
REM 7) Setup subtitles folder
REM ==========================================
if "%TJR_SUBTITLES%"=="" (
    echo [INFO] TJR_SUBTITLES environment variable is not set.
    echo.
    set /p SUBDIR="Enter your subtitles folder path [C:\TJR_SUBTITLES]: "
    if "!SUBDIR!"=="" set SUBDIR=C:\TJR_SUBTITLES

    if not exist "!SUBDIR!" (
        echo [INFO] Creating folder: !SUBDIR!
        mkdir "!SUBDIR!"
    )

    echo [INFO] Setting TJR_SUBTITLES environment variable...
    setx TJR_SUBTITLES "!SUBDIR!" >nul
    set TJR_SUBTITLES=!SUBDIR!
    echo [OK] TJR_SUBTITLES = !SUBDIR!
    echo.
) else (
    echo [OK] TJR_SUBTITLES already set: %TJR_SUBTITLES%
    echo.
)

REM ==========================================
REM Done
REM ==========================================
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
echo NOTE: If ffmpeg was just installed, restart your terminal.
echo.
pause
