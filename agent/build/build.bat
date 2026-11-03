@echo off

REM Build script for Employee Screen Monitor agent executable

setlocal enabledelayedexpansion

set "PROJECT_DIR=%~dp0.."
set "BUILD_DIR=%PROJECT_DIR%\\build"
set "AGENT_DIR=%PROJECT_DIR%\\agent"

cd /d "%AGENT_DIR%"

REM Create build directory
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Installing PyInstaller...
    python -m pip install pyinstaller
)

REM Build the executable
pyinstaller --onefile --windowed main.py --icon=icon.ico --name=main

if errorlevel 0 (
    echo Build successful!
    echo Executable created in "%BUILD_DIR%\\dist\\main.exe"
) else (
    echo Build failed!
)

pause