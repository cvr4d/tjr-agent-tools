@echo off
setlocal enabledelayedexpansion
chcp 65001 >nul

REM --- Check virtual environment ---
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found.
    echo Please run install.bat first.
    echo.
    pause
    exit /b 1
)

REM --- Activate venv ---
call venv\Scripts\activate.bat

REM --- Show usage if no arguments ---
if "%~1"=="" goto :usage

REM --- Route command ---
set "CMD=%~1"
shift

if /i "%CMD%"=="context" (
    python tjr_context.py %1 %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%CMD%"=="fuzzy" (
    python tjr_fuzzy.py %1 %2 %3 %4 %5 %6 %7 %8 %9
    goto :end
)

if /i "%CMD%"=="sub" (
    if "%~1"=="" (
        echo Usage: run.bat sub video.mp4 [max_words]
        goto :end
    )
    python sub.py %1 %2
    goto :end
)

if /i "%CMD%"=="frame" (
    if "%~1"=="" (
        echo Usage: run.bat frame video.mp4 [output.mp4]
        goto :end
    )
    python frame.py %1 %2
    goto :end
)

if /i "%CMD%"=="help" goto :usage
if /i "%CMD%"=="-h"   goto :usage
if /i "%CMD%"=="--help" goto :usage

echo [ERROR] Unknown command: %CMD%
echo.
goto :usage

:usage
echo ============================================
echo   TJR Agent Tools
echo ============================================
echo.
echo Usage:
echo   run.bat context "search phrase"
echo   run.bat fuzzy   "search frase"
echo   run.bat sub     video.mp4 [max_words_per_line]
echo   run.bat frame   video.mp4 [output.mp4]
echo   run.bat help
echo.
echo Examples:
echo   run.bat context "fair value gap"
echo   run.bat fuzzy   "fair value gapp"
echo   run.bat sub     C:\Videos\clip.mp4 5
echo   run.bat frame   C:\Videos\clip.mp4
echo.

:end
endlocal
