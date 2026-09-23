@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

echo ============================================
echo   TJR Agent Tools - Full Auto Installer
echo ============================================
echo.
echo This will install:
echo   - yt-dlp
echo   - ffmpeg (downloaded automatically)
echo   - Python packages (rapidfuzz, Pillow, faster-whisper)
echo   - Whisper model (small, ~500 MB)
echo.
echo Estimated time: 5-15 minutes (depends on internet)
echo.
pause
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
REM 3) Install yt-dlp globally
REM ==========================================
where yt-dlp >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing yt-dlp...
    python -m pip install --upgrade yt-dlp
    if !errorlevel! neq 0 (
        echo [WARNING] Failed to install yt-dlp.
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
    echo [WARNING] ffmpeg not found.

    if exist "C:\ffmpeg\bin\ffmpeg.exe" (
        echo [INFO] Found ffmpeg at C:\ffmpeg\bin
        setx PATH "%PATH%;C:\ffmpeg\bin" >nul
        set "PATH=%PATH%;C:\ffmpeg\bin"
        echo [OK] ffmpeg added to PATH.
    ) else (
        echo [INFO] Downloading ffmpeg...

        where curl >nul 2>nul
        if !errorlevel! neq 0 (
            echo [ERROR] curl not found. Install ffmpeg manually.
            goto :skip_ffmpeg
        )

        set "FFMPEG_ZIP=%TEMP%\ffmpeg.zip"
        curl -L -o "!FFMPEG_ZIP!" "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        if !errorlevel! neq 0 (
            echo [ERROR] Download failed.
            goto :skip_ffmpeg
        )

        echo [INFO] Extracting...
        if exist "C:\ffmpeg" rmdir /s /q "C:\ffmpeg"
        mkdir "C:\ffmpeg_temp"
        tar -xf "!FFMPEG_ZIP!" -C "C:\ffmpeg_temp"

        for /d %%D in ("C:\ffmpeg_temp\ffmpeg-*") do (
            move "%%D" "C:\ffmpeg" >nul
            goto :moved
        )
        :moved
        rmdir /s /q "C:\ffmpeg_temp"
        del "!FFMPEG_ZIP!"

        setx PATH "%PATH%;C:\ffmpeg\bin" >nul
        set "PATH=%PATH%;C:\ffmpeg\bin"
        echo [OK] ffmpeg installed.
        echo [WARNING] Restart terminal for PATH to take effect.
    )
    echo.
) else (
    echo [OK] ffmpeg already installed.
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
        echo [ERROR] Failed to create venv.
        pause
        exit /b 1
    )
    echo [OK] venv created.
    echo.
) else (
    echo [INFO] venv already exists.
    echo.
)

REM ==========================================
REM 6) Install Python packages
REM ==========================================
echo [INFO] Installing Python packages (this may take a few minutes)...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Package installation failed.
    pause
    exit /b 1
)
echo [OK] Packages installed.
echo.

REM ==========================================
REM 7) Pre-download Whisper model
REM ==========================================
echo [INFO] Pre-downloading Whisper model (small, ~500 MB)...
echo       This may take 5-10 minutes depending on your internet.
echo       Please be patient...
echo.

python -c "from faster_whisper import WhisperModel; print('Downloading model...'); WhisperModel('small', device='cpu', compute_type='int8'); print('Model ready!')"

if %errorlevel% neq 0 (
    echo.
    echo [WARNING] Model download failed.
    echo It will download automatically on first use of sub.py.
) else (
    echo [OK] Whisper model downloaded and cached.
)
echo.

REM ==========================================
REM 8) Setup subtitles folder
REM ==========================================
if "%TJR_SUBTITLES%"=="" (
    echo [INFO] TJR_SUBTITLES environment variable is not set.
    echo.
    set /p SUBDIR="Enter your subtitles folder path [C:\TJR_SUBTITLES]: "
    if "!SUBDIR!"=="" set SUBDIR=C:\TJR_SUBTITLES

    if not exist "!SUBDIR!" (
        mkdir "!SUBDIR!"
    )

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
echo All tools are ready:
echo   run.bat context "your phrase"
echo   run.bat fuzzy   "your frase"
echo   run.bat sub     video.mp4 5
echo   run.bat frame   video.mp4
echo.
echo If ffmpeg was just installed, restart your terminal.
echo.
pause
